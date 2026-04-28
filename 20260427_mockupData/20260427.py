import pandas as pd
import random
import os
from datetime import datetime

# ==========================================
# 설정 변수 (파일 경로 및 이름)
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILENAME = os.path.join(BASE_DIR, '2026-04-27T01-51_export.csv')

# 실행 시점의 시간을 포함하여 출력 파일명 생성 (예: mockup_asset_evaluation_20260427_153022.csv)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_FILENAME = os.path.join(BASE_DIR, f'mockup_asset_evaluation_{timestamp}.csv')

def generate_manufacturing_mockup(input_file, output_file):
    """
    제조업 기반 IT 자산 평가 목업 데이터를 생성하고 상세 의견을 도출하는 함수
    """
    if not os.path.exists(input_file):
        print(f"오류: '{input_file}' 파일이 존재하지 않습니다.")
        return

    # CSV 파일 로드
    df = pd.read_csv(input_file)

    # 1. 등급별 분류 기준 정의
    # [중요도 상] 필수 키워드: 이 자산들만 5점이 포함될 수 있으며 '상' 등급(평균 4.0 이상)이 가능함
    high_score_keywords = ["서버", "네트워크 장비", "네트워킹장비", "라우터", "센터", "스위치"]
    # [중요도 중] 필수 부서: 이 부서들은 최소 '중' 등급(평균 3.0~3.9)을 보장하며 5점은 허용하지 않음
    important_depts = ["설계", "전산", "연구", "품질"]

    def process_row(row):
        asset_name = str(row['자산명'])
        dept_name = str(row['부서명/제조사'])
        
        is_high_asset = any(kw in asset_name for kw in high_score_keywords)
        is_important_dept = any(kw in dept_name for kw in important_depts)

        # 2. 등급별 점수 생성 로직 (5점 노출 제어 및 경계값 엄격 관리)
        if is_high_asset:
            # [상 등급] 4~5점을 사용하며 평균 4.0 ~ 5.0 (합계 20~25) 유지
            scores = [random.randint(4, 5) for _ in range(5)]
            if sum(scores) < 20: scores[0] = 4 # 최소 합계 20점 보장
        
        elif is_important_dept:
            # [중 등급 고정] 개별 항목 최대 4점으로 제한 (5점 방지), 평균 3.0 ~ 3.8 (합계 15~19)
            scores = [random.randint(3, 4) for _ in range(5)]
            
            # 합계가 20(평균 4.0)이 되어 '상'으로 판정되는 것을 방지하기 위해 강제 조정
            while sum(scores) >= 20:
                idx = random.randint(0, 4)
                if scores[idx] == 4:
                    scores[idx] = 3
            
            # 합계가 15 미만이면 '하'가 되므로 최소 15점 보장
            while sum(scores) < 15:
                idx = random.randint(0, 4)
                if scores[idx] == 3:
                    scores[idx] = 4
        
        else:
            # [일반 자산] 개별 항목 최대 4점으로 제한 (5점 방지), 평균 1.0 ~ 3.8 (합계 5~19)
            scores = [random.randint(1, 4) for _ in range(5)]
            
            # 일반 자산이 20점 이상이 되어 '상'이 되지 않도록 제한
            while sum(scores) >= 20:
                idx = random.randint(0, 4)
                if scores[idx] > 1:
                    scores[idx] -= 1

        # 점수 적용
        score_cols = ['기밀성', '무결성', '가용성', '업무기여도', '컴플라이언스']
        for col, val in zip(score_cols, scores):
            row[col] = val

        # 3. 최종 평가점수 및 등급 판정
        avg_score = round(sum(scores) / 5, 1)
        row['평가점수'] = avg_score

        # 등급 판정
        if avg_score >= 4.0:
            level = "상"
        elif avg_score >= 3.0:
            level = "중"
        else:
            level = "하"

        # 4. 상세 의견 생성
        opinion = ""
        if level == "상":
            reason = "전사 인프라의 핵심 접점으로 장애 시 생산 라인 및 전 부서 업무가 마비되는 치명적인 영향을 미침."
            opinion = f"[중요도 상] {reason} 집중 관리 및 실시간 모니터링 대상임."

        elif level == "중":
            if is_important_dept:
                reason = f"{dept_name} 부서의 핵심 기술 데이터 및 지적 재산을 직접 취급하는 단말로 보안 관리가 필수적임."
            else:
                reason = f"{dept_name} 업무의 연속성 유지를 위한 주요 자산으로 관리 가치가 있음."
            opinion = f"[중요도 중] {reason} 정기 점검 및 보안 수칙 준수가 요구됨."

        else: # 중요도 하
            reason = "일반 사무 보조 및 단순 조회용 자산으로, 장애 시 비즈니스 영향도가 낮으며 대체가 용이함."
            opinion = f"[중요도 하] {reason} 기본적인 자산 관리 절차에 따라 운영함."

        row['의견'] = opinion
        return row

    # 데이터 변환 실행
    print(f"데이터 처리 시작 (입력: {input_file})")
    df = df.apply(process_row, axis=1)

    # 5. 결과 저장 (Excel 호환을 위한 utf-8-sig 인코딩)
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"작업 완료: '{output_file}' 파일이 성공적으로 생성되었습니다.")

if __name__ == "__main__":
    generate_manufacturing_mockup(INPUT_FILENAME, OUTPUT_FILENAME)