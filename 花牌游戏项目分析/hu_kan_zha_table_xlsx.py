#!/usr/bin/env python3
"""生成 精牌坎牌扎牌招牌查表汇总.xlsx — 坎牌(3张) + 扎牌/招牌(4张) 查表（红精+黑精+非精基础+说明）
主精 = 非主精 × 2，用公式自动计算。
"""
import os
import sys

sys.path.insert(0, os.path.join(os.getenv("SKILL_PATH"), "xlsx", "scripts"))
from recalc import recalc

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "精牌坎牌扎牌招牌查表汇总.xlsx")

FONT = "微软雅黑"
HDR_FILL = "C00000"
MAIN_ROW_FILL = "FFF2CC"


def _style_header(cell):
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    cell.font = Font(name=FONT, size=11, bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor=HDR_FILL)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    thin = Side(style="thin", color="D9D9D9")
    cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)


def _style_cell(cell, center=True, bold=False, fill=None):
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    cell.font = Font(name=FONT, size=11, bold=bold)
    cell.alignment = Alignment(horizontal="center" if center else "left",
                               vertical="center", wrap_text=True)
    if fill:
        cell.fill = PatternFill("solid", fgColor=fill)
    thin = Side(style="thin", color="D9D9D9")
    cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)


def _build_type_sheet(wb, title, subtitle, headers, rows, chart_anchor, chart_title):
    """通用：构建一个 红精 查表 Sheet + 柱状图"""
    from openpyxl.styles import Font, Alignment
    from openpyxl.chart import BarChart, Reference
    ws = wb.create_sheet(title)

    ws.merge_cells("A1:G1")
    c = ws["A1"]
    c.value = subtitle + " — 8 种可达组合" if len(rows) == 8 else subtitle
    c.font = Font(name=FONT, size=14, bold=True, color="C00000")
    c.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 26

    ws.merge_cells("A2:G2")
    c = ws["A2"]
    c.value = "主精 = 非主精 × 2（公式自动计算）；每种精牌最多 3皮2花、赖子全局最多 2 张"
    c.font = Font(name=FONT, size=10, italic=True, color="808080")
    c.alignment = Alignment(horizontal="center", vertical="center")

    for j, h in enumerate(headers, 1):
        _style_header(ws.cell(row=3, column=j, value=h))
    ws.row_dimensions[3].height = 22

    max_v = max(r[4] for r in rows)
    for i, r in enumerate(rows):
        rr = 4 + i
        fill = MAIN_ROW_FILL if r[4] == max_v else None
        _style_cell(ws.cell(row=rr, column=1, value=r[0]), fill=fill)
        _style_cell(ws.cell(row=rr, column=2, value=r[1]), fill=fill)
        _style_cell(ws.cell(row=rr, column=3, value=r[2]), fill=fill)
        _style_cell(ws.cell(row=rr, column=4, value=r[3]), fill=fill)
        _style_cell(ws.cell(row=rr, column=5, value=r[4]), fill=fill)
        _style_cell(ws.cell(row=rr, column=6, value=f"=E{rr}*2"), fill=fill)
        _style_cell(ws.cell(row=rr, column=7, value=r[5]), fill=fill)
        ws.row_dimensions[rr].height = 20

    for col, w in zip("ABCDEFG", [14, 8, 8, 8, 10, 10, 20]):
        ws.column_dimensions[col].width = w

    # 柱状图：非主精 vs 主精
    chart = BarChart()
    chart.type = "bar"
    chart.style = 10
    chart.title = chart_title
    chart.y_axis.title = "组合"
    chart.x_axis.title = "胡数"
    chart.legend.position = "b"
    data = Reference(ws, min_col=5, min_row=3, max_col=6, max_row=3 + len(rows))
    cats = Reference(ws, min_col=1, min_row=4, max_row=3 + len(rows))
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    chart.height = 8.5
    chart.width = 18
    ws.add_chart(chart, chart_anchor)
    return ws


def build_red_kan_sheet(wb):
    headers = ["组合", "皮数", "花数", "赖数", "非主精", "主精", "JS key（花_皮_赖）"]
    rows = [
        ("1花2赖",    0, 1, 2, 12, "1_0_2"),
        ("2花1赖",    0, 2, 1, 9,  "2_0_1"),
        ("1皮2花",    1, 2, 0, 7,  "2_1_0"),
        ("1皮1花1赖", 1, 1, 1, 7,  "1_1_1"),
        ("1皮2赖",    1, 0, 2, 7,  "0_1_2"),
        ("2皮1花",    2, 1, 0, 6,  "1_2_0"),
        ("2皮1赖",    2, 0, 1, 6,  "0_2_1"),
        ("3皮",       3, 0, 0, 5,  "0_3_0"),
    ]
    _build_type_sheet(wb, "红精坎牌", "红精（三/五/七）坎牌查表", headers, rows, "I3", "红精坎牌胡数对比（非主精 vs 主精）")


def build_red_zha_sheet(wb):
    headers = ["组合", "皮数", "花数", "赖数", "非主精", "主精", "JS key（花_皮_赖）"]
    rows = [
        ("2花2赖",    0, 2, 2, 24, "2_0_2"),
        ("1皮1花2赖", 1, 1, 2, 18, "1_1_2"),
        ("1皮2花1赖", 1, 2, 1, 18, "2_1_1"),
        ("2皮2花",    2, 2, 0, 14, "2_2_0"),
        ("2皮2赖",    2, 0, 2, 14, "0_2_2"),
        ("2皮1花1赖", 2, 1, 1, 14, "1_2_1"),
        ("3皮1花",    3, 1, 0, 12, "1_3_0"),
        ("3皮1赖",    3, 0, 1, 12, "0_3_1"),
    ]
    _build_type_sheet(wb, "红精扎牌招牌", "红精（三/五/七）扎牌 / 招牌查表", headers, rows, "I3", "红精扎牌招牌胡数对比（非主精 vs 主精）")


def build_black_sheet(wb):
    from openpyxl.styles import Font, Alignment
    ws = wb.create_sheet("黑精与基础")

    ws.merge_cells("A1:F1")
    c = ws["A1"]
    c.value = "黑精（乙/九）坎牌 / 扎牌 / 招牌查表 + 非精字面基础胡"
    c.font = Font(name=FONT, size=14, bold=True, color="C00000")
    c.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 26

    ws.merge_cells("A2:F2")
    c = ws["A2"]
    c.value = "黑精无赖子组合（赖子不能通配乙/九）"
    c.font = Font(name=FONT, size=10, italic=True, color="808080")
    c.alignment = Alignment(horizontal="center", vertical="center")

    # ---- 黑精坎 ----
    ws.merge_cells("A4:F4")
    c = ws["A4"]
    c.value = "黑精坎牌（3张）"
    c.font = Font(name=FONT, size=12, bold=True)
    headers = ["组合", "皮数", "花数", "胡数", "JS key（花_皮_赖）"]
    for j, h in enumerate(headers, 1):
        _style_header(ws.cell(row=5, column=j, value=h))
    kan_rows = [
        ("1皮2花", 1, 2, 3, "2_1_0"),
        ("2皮1花", 2, 1, 2, "1_2_0"),
        ("3皮",    3, 0, 1, "0_3_0"),
    ]
    for i, (combo, p, f, hu, key) in enumerate(kan_rows):
        rr = 6 + i
        _style_cell(ws.cell(row=rr, column=1, value=combo))
        _style_cell(ws.cell(row=rr, column=2, value=p))
        _style_cell(ws.cell(row=rr, column=3, value=f))
        _style_cell(ws.cell(row=rr, column=4, value=hu))
        _style_cell(ws.cell(row=rr, column=5, value=key))

    # ---- 黑精扎/招 ----
    ws.merge_cells("A10:F10")
    c = ws["A10"]
    c.value = "黑精扎牌 / 招牌（4张，共用一张表）"
    c.font = Font(name=FONT, size=12, bold=True)
    for j, h in enumerate(headers, 1):
        _style_header(ws.cell(row=11, column=j, value=h))
    zha_rows = [
        ("3皮1花", 3, 1, 3, "1_3_0"),
        ("2皮2花", 2, 2, 4, "2_2_0"),
    ]
    for i, (combo, p, f, hu, key) in enumerate(zha_rows):
        rr = 12 + i
        _style_cell(ws.cell(row=rr, column=1, value=combo))
        _style_cell(ws.cell(row=rr, column=2, value=p))
        _style_cell(ws.cell(row=rr, column=3, value=f))
        _style_cell(ws.cell(row=rr, column=4, value=hu))
        _style_cell(ws.cell(row=rr, column=5, value=key))

    # ---- 黑精不能当主精说明 ----
    ws.merge_cells("A15:E15")
    c = ws["A15"]
    c.value = "注：黑精（乙/九）不能作为主精（游戏规则限制），恒按非主精计胡，无主精翻倍。"
    c.font = Font(name=FONT, size=9, color="C00000")
    c.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[15].height = 16

    # ---- 非精字面基础胡 ----
    ws.merge_cells("A17:F17")
    c = ws["A17"]
    c.value = "非精字面基础胡（无精牌加成）"
    c.font = Font(name=FONT, size=12, bold=True)
    _style_header(ws.cell(row=18, column=1, value="牌型"))
    _style_header(ws.cell(row=18, column=2, value="红字面"))
    _style_header(ws.cell(row=18, column=3, value="黑字面"))
    for j in range(4, 7):
        _style_header(ws.cell(row=18, column=j, value=""))
    base_rows = [
        ("坎牌（3张）", 2, 1),
        ("扎牌/招牌（4张）", 4, 2),
    ]
    for i, (name, red, black) in enumerate(base_rows):
        rr = 19 + i
        _style_cell(ws.cell(row=rr, column=1, value=name))
        _style_cell(ws.cell(row=rr, column=2, value=red))
        _style_cell(ws.cell(row=rr, column=3, value=black))
        for j in range(4, 7):
            _style_cell(ws.cell(row=rr, column=j, value=""))

    for col, w in zip("ABCDEF", [16, 8, 8, 10, 10, 20]):
        ws.column_dimensions[col].width = w


def build_note_sheet(wb):
    from openpyxl.styles import Font, Alignment
    ws = wb.create_sheet("说明")
    ws.column_dimensions["A"].width = 6
    ws.column_dimensions["B"].width = 90

    rows = [
        ("适用范围", [
            "坎牌 = 3 张同字（手中暗牌，可灵活调整）",
            "扎牌（暗杠）= 招牌（明杠）= 4 张同字，共用一张表，胡数相同",
            "主精 = 非主精 × 2（红精、黑精均成立）",
            "每种精牌最多 3皮 + 2花；赖子全局最多 2 张",
            "赖子只能通配三/五/七（红精），不能配乙/九（黑精）",
            "招牌（明牌）不参与赖子；扎牌（暗杠）可含赖子，两者共用表无冲突",
        ]),
        ("代码位置", [
            "JS 红精表：JING_RED_TABLE['kan'] / ['zhao']（step5-hu.html）",
            "JS 黑精表：JING_BLACK_TABLE['kan'] / ['zhao']（step5-hu.html）",
            "Python 红精表：_RED_JING_KAN_TABLE / _RED_JING_ZHA_TABLE（计分引擎v3.py）",
            "Python 黑精表：_BLACK_JING_KAN_TABLE / _BLACK_JING_ZHA_TABLE（计分引擎v3.py）",
            "校验：test_hu_tables_complete.js（含坎/扎/招全部组合）",
        ]),
        ("历史坑", [
            "JS 红精 kan 表曾缺纯精 3 条（1皮2花/2皮1花/3皮），靠兜底线性算对，2026-08-24 已补齐",
            "JS 黑精 kan 表 key 曾为死条目（从未命中靠兜底），2026-08-24 已修正",
            "今后改动查表，请运行 bash hu_tests/run_all.sh 一键回归",
        ]),
    ]
    r = 1
    for title, items in rows:
        ws.merge_cells(f"B{r}:B{r}")
        c = ws.cell(row=r, column=2, value=title)
        c.font = Font(name=FONT, size=13, bold=True, color="C00000")
        ws.row_dimensions[r].height = 20
        r += 1
        for it in items:
            ws.merge_cells(f"B{r}:B{r}")
            c = ws.cell(row=r, column=2, value="· " + it)
            c.font = Font(name=FONT, size=11)
            c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
            ws.row_dimensions[r].height = 18
            r += 1
        r += 1


def main():
    from openpyxl import Workbook
    wb = Workbook()
    wb.remove(wb.active)
    build_red_kan_sheet(wb)
    build_red_zha_sheet(wb)
    build_black_sheet(wb)
    build_note_sheet(wb)
    wb.save(OUTPUT)
    print("saved:", OUTPUT)


if __name__ == "__main__":
    main()
    result = recalc(OUTPUT)
    print(result)
    if result.get("status") != "success":
        raise SystemExit(1)
