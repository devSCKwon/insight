import os
import pandas as pd
from pptx import Presentation
from copy import deepcopy

def duplicate_slide(pres, index):
    """
    템플릿 슬라이드를 복제하여 새로운 슬라이드를 생성합니다.
    (python-pptx는 직접적인 슬라이드 복제 기능을 제공하지 않아 요소를 복사하는 방식 사용)
    """
    template_slide = pres.slides[index]
    slide_layout = template_slide.slide_layout
    new_slide = pres.slides.add_slide(slide_layout)
    
    # 1. 레이아웃에 의해 자동 생성된 기본 도형(Placeholder)들 제거
    # 복사될 도형들과 겹치지 않게 하기 위함입니다.
    for shape in list(new_slide.shapes):
        sp = shape.element
        sp.getparent().remove(sp)
    
    # 2. 템플릿 슬라이드의 모든 도형 복사
    for shape in template_slide.shapes:
        el = shape.element
        new_el = deepcopy(el)
        new_slide.shapes._spTree.insert_element_before(new_el, 'p:extLst')
    
    return new_slide

def replace_text_preserve_style(shape, old_text, new_text):
    """도형 내의 텍스트를 서식을 유지하며 치환합니다."""
    if not shape.has_text_frame:
        return
    for paragraph in shape.text_frame.paragraphs:
        for run in paragraph.runs:
            if old_text in run.text:
                run.text = run.text.replace(old_text, new_text)

def set_cell_text_preserve_style(cell, text):
    """테이블 셀의 텍스트를 서식을 유지하며 변경합니다."""
    if not cell.text_frame.paragraphs:
        cell.text = text
        return
    paragraph = cell.text_frame.paragraphs[0]
    if not paragraph.runs:
        paragraph.add_run().text = text
    else:
        # 첫 번째 Run의 텍스트를 변경하고 나머지는 비워서 스타일 유지
        paragraph.runs[0].text = text
        for i in range(1, len(paragraph.runs)):
            r = paragraph.runs[i]
            r.text = ""

def run_automation(excel_file, template_file, output_file):
    # 1. 엑셀 데이터와 PPT 템플릿 로드
    df = pd.read_excel(excel_file)
    # 컬럼명 인코딩 이슈를 방지하기 위해 강제로 컬럼명을 지정합니다.
    # 순서: 부서명, 카테고리, 평가구분, 항목번호, 점검문항내용 ...
    new_cols = ['부서명', '카테고리', '평가구분', '점검 문항 내용']
    # 실제 컬럼 수가 더 많을 수 있으므로 존재하는 만큼만 덮어씌웁니다.
    df.columns = new_cols + list(df.columns[len(new_cols):])
    
    prs = Presentation(template_file)
    
    # 2. 엑셀의 각 행(Row) 데이터를 순회하며 슬라이드 생성
    for _, row in df.iterrows():
        # 첫 번째 슬라이드(index 0)를 복제
        new_slide = duplicate_slide(prs, 0)
        
        # 3. 슬라이드 내의 도형(Shape)들 탐색
        for shape in new_slide.shapes:
            # 제목 등의 일반 텍스트 치환 (서식 유지)
            replace_text_preserve_style(shape, "{부서명}", str(row['부서명']))
            
            # 테이블 데이터 입력 (행 2개 이상, 열 3개인 주 테이블 대상)
            if shape.has_table:
                table = shape.table
                if len(table.rows) >= 2 and len(table.columns) >= 3:
                    # 엑셀 열 이름에 맞춰서 테이블 셀(Row, Col)에 값 입력 (서식 유지)
                    set_cell_text_preserve_style(table.cell(1, 0), str(row['카테고리']))
                    set_cell_text_preserve_style(table.cell(1, 1), str(row['평가구분']))
                    set_cell_text_preserve_style(table.cell(1, 2), str(row['점검 문항 내용']))

    # 4. 맨 앞에 남아있는 원본 템플릿 슬라이드 삭제
    xml_slides = prs.slides._sldIdLst
    xml_slides.remove(xml_slides[0])
    
    # 5. 최종 결과 저장
    prs.save(output_file)
    print(f"작업 완료! 생성된 파일: {output_file}")

# 실행부
if __name__ == "__main__":
    # 스크립트 파일의 디렉토리 경로를 가져옵니다.
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # 파일 경로 설정 (절대 경로로 변환)
    EXCEL_PATH = os.path.join(BASE_DIR, '평가지표.xlsx')
    TEMPLATE_PATH = os.path.join(BASE_DIR, '진단평가시트_20260428.pptx')
    OUTPUT_PATH = os.path.join(BASE_DIR, 'Final_Report.pptx')
    
    run_automation(EXCEL_PATH, TEMPLATE_PATH, OUTPUT_PATH)