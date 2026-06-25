import os
import re
from datetime import datetime
from pptx import Presentation

def get_slide_text(slide):
    """슬라이드 내의 모든 텍스트를 추출"""
    text = []
    for shape in slide.shapes:
        if hasattr(shape, "text") and shape.text:
            text.append(shape.text)
    return "\n".join(text)

def extract_category(slide, slide_index):
    """슬라이드 내의 표나 텍스트에서 카테고리명 추출 (강화 버전)"""
    
    # 탐색 대상: 현재 슬라이드의 도형 + 슬라이드 레이아웃의 도형
    target_shapes = list(slide.shapes)
    if hasattr(slide, "slide_layout"):
        target_shapes.extend(list(slide.slide_layout.shapes))

    # 1. 표(Table) 구조에서 찾기
    for shape in target_shapes:
        if shape.has_table:
            table = shape.table
            for r, row in enumerate(table.rows):
                for c, cell in enumerate(row.cells):
                    # 모든 공백, 줄바꿈 제거 후 비교
                    clean_text = cell.text.replace(" ", "").replace("\n", "").replace("\r", "")
                    if "평가구분" in clean_text:
                        try:
                            # '평가 구분' 셀을 찾았으면, 바로 아래 행들 중에서 텍스트가 있는 첫 번째 셀 추출
                            for next_r in range(r + 1, len(table.rows)):
                                category = table.cell(next_r, c).text.strip()
                                if category:
                                    print(f"[디버그] 슬라이드 {slide_index+1}: 표에서 '{category}' 추출 성공")
                                    return re.sub(r'[\/:*?"<>|]', "_", category)
                        except Exception as e:
                            print(f"[디버그] 슬라이드 {slide_index+1}: 표 분석 중 오류 - {e}")

    # 2. 일반 텍스트에서 찾기 (정규식 강화)
    full_text = ""
    for shape in target_shapes:
        if hasattr(shape, "text") and shape.text:
            full_text += shape.text + "\n"
    
    # 줄바꿈 무시하고 패턴 찾기
    clean_full_text = full_text.replace(" ", "")
    match = re.search(r"평가구분[:：]?([^\n]+)", clean_full_text)
    if match:
        category = match.group(1).strip()
        print(f"[디버그] 슬라이드 {slide_index+1}: 텍스트에서 '{category}' 추출 성공")
        return re.sub(r'[\/:*?"<>|]', "_", category)
        
    return None

def split_by_category(source_pptx, base_result_dir):
    """슬라이드 내용을 분석하여 카테고리별로 분할 저장"""
    prs = Presentation(source_pptx)
    
    # 1. 슬라이드별 카테고리 매핑
    slide_groups = {} # {category_name: [slide_indices]}
    current_category = "기타(분류불가)"
    
    for i, slide in enumerate(prs.slides):
        found_category = extract_category(slide, i)
        
        # 새로운 카테고리가 발견되면 업데이트, 없으면 이전 카테고리 유지
        if found_category:
            current_category = found_category
            
        if current_category not in slide_groups:
            slide_groups[current_category] = []
        slide_groups[current_category].append(i)

    if not slide_groups:
        print("카테고리를 찾을 수 없습니다.")
        return

    # 2. 결과 폴더 생성 (날짜 시퀀스)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(base_result_dir, timestamp)
    os.makedirs(output_dir, exist_ok=True)
    print(f"결과 저장 폴더: {output_dir}")

    # 3. 각 그룹별로 저장
    for category, indices in slide_groups.items():
        # 원본 다시 로드
        new_prs = Presentation(source_pptx)
        
        # 삭제할 슬라이드 인덱스 계산 (내림차순으로 처리해야 인덱스가 변하지 않음)
        all_indices = list(range(len(new_prs.slides)))
        to_delete_indices = sorted(list(set(all_indices) - set(indices)), reverse=True)
        
        # 슬라이드 제거 및 관련 리소스 정리
        for idx in to_delete_indices:
            rId = new_prs.slides._sldIdLst[idx].rId
            # 1. Presentation 파트에서 해당 슬라이드와의 관계 제거
            new_prs.part.drop_rel(rId)
            # 2. 슬라이드 리스트에서 ID 제거
            del new_prs.slides._sldIdLst[idx]
            
        output_path = os.path.join(output_dir, f"{category}.pptx")
        new_prs.save(output_path)
        print(f"저장 완료: {category}.pptx (슬라이드 수: {len(indices)}, 용량 최적화 적용)")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SOURCE_DIR = os.path.join(BASE_DIR, "source")
    RESULT_DIR = os.path.join(BASE_DIR, "result")

    source_files = [f for f in os.listdir(SOURCE_DIR) if f.endswith('.pptx') and not f.startswith('~$')]
    
    if not source_files:
        print(f"알림: '{SOURCE_DIR}' 폴더에 원본 PPTX 파일을 넣어주세요.")
    else:
        source_path = os.path.join(SOURCE_DIR, source_files[0])
        print(f"분석 시작: {source_path}")
        try:
            split_by_category(source_path, RESULT_DIR)
            print("\n자동 분류 및 분할이 완료되었습니다.")
        except Exception as e:
            print(f"오류 발생: {e}")
