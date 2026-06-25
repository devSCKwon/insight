import re
import pymupdf  # 임포트 이름 충돌을 방지하기 위해 pymupdf를 직접 사용합니다.


def is_table_or_non_text_block(block, page_drawings, page_height):
    """블록이 테이블(표), 이미지 또는 비정상적인 구조인지 판별하는 헬퍼 함수."""
    # 1. 이미지 블록 필터링
    if block.get("type") != 0:  # 0이 아닌 경우 텍스트 블록이 아님 (이미지 등)
        return True

    block_rect = pymupdf.Rect(block["bbox"])
    block_text = ""
    lines = block.get("lines", [])

    # 블록 내의 모든 텍스트 병합 및 가로 정렬 분석
    line_y_coords = []
    for line in lines:
        line_text = "".join([span["text"] for span in line.get("spans", [])])
        block_text += line_text + "\n"
        line_y_coords.append(line["bbox"][1])  # y0 좌표 저장

    # 2. 빈 블록 예외 처리
    clean_text = block_text.strip()
    if not clean_text:
        return True

    # 3. 표 감지 알고리즘 (Heuristics)
    # 3-1. 숫자 및 특수문자 비율이 너무 높은 경우 (통계표 등)
    digit_count = sum(c.isdigit() for c in clean_text)
    alpha_count = sum(c.isalnum() for c in clean_text)
    if alpha_count > 0 and (digit_count / alpha_count) > 0.4:
        return True

    # 3-2. 동일한 Y축(높이) 상에 멀리 떨어져 있는 텍스트 스팬이 많은 경우 (다단 구조 표)
    for line in lines:
        spans = line.get("spans", [])
        if len(spans) >= 3:  # 한 줄에 3개 이상의 분절된 텍스트 영역이 존재할 때
            gaps = [
                spans[i + 1]["bbox"][0] - spans[i]["bbox"][2]
                for i in range(len(spans) - 1)
            ]
            if any(gap > 30 for gap in gaps):  # 열 사이 간격이 넓은 경우 표로 의심
                return True

    # 3-3. 특정 표 관련 키워드 등장 시 정지
    table_indicators = ["표 ", "table", "그림", "fig.", "대조표", "일정표"]
    if any(indicator in clean_text.lower() for indicator in table_indicators):
        return True

    # 4. 벡터 드로잉(테이블 테두리선, 구분선) 존재 여부 체크
    # 현재 블록 근처나 바로 아래에 가로막는 선이 있는지 확인
    for drawing in page_drawings:
        draw_rect = pymupdf.Rect(drawing["rect"])
        # 드로잉 영역이 선(두께가 얇고 가로로 긴 형태)인지 확인
        if draw_rect.width > 120 and draw_rect.height < 10:
            # 선이 블록 내부 혹은 블록 바로 밑(20포인트 이내)에 위치하는지 검사
            if (
                block_rect.y0 - 5
                <= draw_rect.y0
                <= block_rect.y1 + 20
            ):
                return True

    return False


def smart_highlight_pdf(input_pdf, output_pdf, keyword):
    """사용자 지정 키워드부터 문단 끝(혹은 표 시작 전)까지 스마트 하이라이트를 수행합니다."""
    doc = pymupdf.open(input_pdf)
    highlight_count = 0

    for page_idx in range(len(doc)):
        page = doc[page_idx]

        # 1. 키워드 검색 (가장 먼저 매칭되는 지점 탐색)
        search_results = page.search_for(keyword)
        if not search_results:
            continue

        # 첫 번째 검색 결과를 기준으로 삼음
        keyword_rect = search_results[0]

        # 2. 페이지 내의 모든 그래픽 드로잉 정보 가져오기 (표 구분선 감지용)
        drawings = page.get_drawings()

        # 3. 페이지의 상세 레이아웃 구조 분석 (텍스트 딕셔너리 추출)
        page_dict = page.get_text("dict")
        blocks = page_dict.get("blocks", [])

        # 4. 키워드가 위치한 블록과 선(Line) 찾기
        start_block_idx = -1
        start_line_idx = -1
        start_span_idx = -1

        for b_idx, block in enumerate(blocks):
            if block.get("type") != 0:
                continue
            for l_idx, line in enumerate(block.get("lines", [])):
                line_rect = pymupdf.Rect(line["bbox"])
                # 키워드 영역과 라인 영역이 겹치는지 체크
                if line_rect.intersects(keyword_rect):
                    start_block_idx = b_idx
                    start_line_idx = l_idx
                    # 구체적인 스팬(Span) 위치 탐색
                    for s_idx, span in enumerate(line.get("spans", [])):
                        if keyword in span["text"]:
                            start_span_idx = s_idx
                            break
                    break
            if start_block_idx != -1:
                break

        # 키워드 위치를 레이아웃에서 찾지 못한 경우 안전지대로 패스
        if start_block_idx == -1:
            continue

        # 5. 하이라이트 대상 라인 수집하기
        lines_to_highlight = []
        stop_highlighting = False

        for b_idx in range(start_block_idx, len(blocks)):
            block = blocks[b_idx]

            # 현재 블록이 테이블이거나 비텍스트 요소인지 조기 검증
            if b_idx > start_block_idx and is_table_or_non_text_block(
                block, drawings, page.rect.height
            ):
                print(
                    f"[정보] {page_idx + 1}페이지에서 테이블 또는 구분선을 감지하여 하이라이트를 정지했습니다."
                )
                break

            lines = block.get("lines", [])
            start_l = (
                start_line_idx if b_idx == start_block_idx else 0
            )

            for l_idx in range(start_l, len(lines)):
                line = lines[l_idx]
                line_rect = pymupdf.Rect(line["bbox"])

                # 첫 줄일 경우, 키워드가 시작된 스팬 위치의 좌표부터 하이라이트하도록 영역 분할
                if b_idx == start_block_idx and l_idx == start_line_idx:
                    # 키워드 시작 지점의 x0 좌표를 반영하여 줄의 뒷부분만 하이라이트
                    highlight_rect = pymupdf.Rect(
                        keyword_rect.x0,
                        line_rect.y0,
                        line_rect.x1,
                        line_rect.y1,
                    )
                else:
                    highlight_rect = line_rect

                lines_to_highlight.append(highlight_rect)

            # 한 문단(블록) 처리가 끝나면 마칩니다. (다음 블록으로 넘어가기 전 멈춤 보장)
            # 만약 다음 문단까지 계속 이어서 칠하고 싶다면 아래 break를 주석 처리할 수 있습니다.
            # 하지만 '텍스트가 끝나는 지점까지'라는 요구조건과 표 진입 방지를 위해 1개 블록(문단) 단위 완료 후 멈추는 것이 가장 안전합니다.
            break

        # 6. 수집된 영역에 실제로 하이라이트 처리
        for rect in lines_to_highlight:
            # 지나치게 작거나 빈 영역 제외
            if rect.width > 2 and rect.height > 2:
                annot = page.add_highlight_annot(rect)
                annot.set_colors(stroke=(1, 0.9, 0.2))  # 부드러운 파스텔톤 노란색
                annot.update()
                highlight_count += 1

    # 7. 변경 내용 저장
    if highlight_count > 0:
        doc.save(output_pdf)
        print(
            f"✔ 성공: 총 {highlight_count}개의 라인 영역에 형광펜을 정상적으로 칠했습니다."
        )
        print(f"✔ 저장 완료: {output_pdf}")
    else:
        print("⚠ 검색된 키워드가 없거나 하이라이트할 영역을 찾지 못했습니다.")

    doc.close()


if __name__ == "__main__":
    # 실행부
    input_file = "sample.pdf"
    output_file = "sample_highlighted.pdf"

    user_keyword = input("형광펜 시작점으로 지정할 키워드를 입력하세요: ").strip()

    if user_keyword:
        smart_highlight_pdf(input_file, output_file, user_keyword)
    else:
        print("키워드가 올바르게 입력되지 않았습니다.")