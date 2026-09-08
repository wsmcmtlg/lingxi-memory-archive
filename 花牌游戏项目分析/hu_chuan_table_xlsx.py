#!/usr/bin/env python3
"""生成 精牌穿牌查表汇总.xlsx — 精牌穿牌/泛牌查表（红精+黑精+非精基础+说明）
主精 = 非主精 × 2，用公式自动计算。
"""
import os
import sys

sys.path.insert(0, os.path.join(os.getenv("SKILL_PATH"), "xlsx", "scripts"))
from recalc import recalc

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "精牌穿牌查表汇总.xlsx")

# 样式常量
FONT = "微软雅黑"
HDR_FILL = "C00000"          # 深红表头
SUB_FILL = "F2DCDB"          # 浅红子标题
MAIN_ROW_FILL = "FFF2CC"     # 高亮最高行（96）
NOTE_FILL = "F2F2F2"


def _style_header(cell):
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    cell.font = Font(name=FONT, size=11, bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor=HDR_FILL)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    thin = Side(style="thin", color="D9D9D9")
    cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)


def _style_cell(cell, center=True, bold=False, fill=None, numfmt=None):
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    cell.font = Font(name=FONT, size=11, bold=bold)
    cell.alignment = Alignment(horizontal="center" if center else "left",
                               vertical="center", wrap_text=True)
    if fill:
        cell.fill = PatternFill("solid", fgColor=fill)
    if numfmt:
        cell.number_format = numfmt
    thin = Side(style="thin", color="D9D9D9")
    cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)


def build_red_sheet(wb):
    """Sheet1：红精穿/泛 6 条 + 图表"""
    from openpyxl.styles import Font, PatternFill, Alignment
    ws = wb.active
    ws.title = "红精穿泛牌"

    # 标题
    ws.merge_cells("A1:G1")
    c = ws["A1"]
    c.value = "红精（三/五/七）穿牌 / 泛牌查表 — 6 种可达组合"
    c.font = Font(name=FONT, size=14, bold=True, color="C00000")
    c.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 26

    # 子标题说明
    ws.merge_cells("A2:G2")
    c = ws["A2"]
    c.value = "穿牌=泛牌共用一张表；5 张同字（含赖子通配）；主精 = 非主精 × 2（公式自动计算）"
    c.font = Font(name=FONT, size=10, italic=True, color="808080")
    c.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 18

    # 表头（第3行）
    headers = ["组合", "皮数", "花数", "赖数", "非主精", "主精", "JS key（花_皮_赖）"]
    for j, h in enumerate(headers, 1):
        _style_header(ws.cell(row=3, column=j, value=h))
    ws.row_dimensions[3].height = 22

    # 数据（第4~9行）：组合, 皮, 花, 赖, 非主精, 主精(公式), JS key
    rows = [
        ("1皮2花2赖", 1, 2, 2, 48, "2_1_2"),
        ("2皮1花2赖", 2, 1, 2, 36, "1_2_2"),
        ("2皮2花1赖", 2, 2, 1, 36, "2_2_1"),
        ("3皮2赖",    3, 0, 2, 28, "0_3_2"),
        ("3皮1花1赖", 3, 1, 1, 28, "1_3_1"),
        ("3皮2花",    3, 2, 0, 28, "2_3_0"),
    ]
    for i, (combo, p, f, w, notmain, key) in enumerate(rows):
        r = 4 + i
        fill = MAIN_ROW_FILL if notmain == 48 else None  # 最高 96 行高亮
        _style_cell(ws.cell(row=r, column=1, value=combo), fill=fill)
        _style_cell(ws.cell(row=r, column=2, value=p), fill=fill)
        _style_cell(ws.cell(row=r, column=3, value=f), fill=fill)
        _style_cell(ws.cell(row=r, column=4, value=w), fill=fill)
        _style_cell(ws.cell(row=r, column=5, value=notmain), fill=fill)
        _style_cell(ws.cell(row=r, column=6, value=f"=E{r}*2"), fill=fill)  # 主精公式
        _style_cell(ws.cell(row=r, column=7, value=key), fill=fill)
        ws.row_dimensions[r].height = 20

    # 底部提示
    ws.merge_cells("A11:G11")
    c = ws["A11"]
    c.value = "注：f+s+w=5 数学上共 21 种组合，但受「每种精牌最多 3皮2花、赖子全局最多 2 张」约束，物理可达组合恰为 6 种。"
    c.font = Font(name=FONT, size=9, color="808080")
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    ws.row_dimensions[11].height = 16

    # 列宽
    for col, w in zip("ABCDEFG", [14, 8, 8, 8, 10, 10, 22]):
        ws.column_dimensions[col].width = w

    # 图表：红精 6 条 主精/非主精 对比（横向柱状图）
    from openpyxl.chart import BarChart, Reference
    chart = BarChart()
    chart.type = "bar"
    chart.style = 10
    chart.title = "红精穿牌胡数对比（非主精 vs 主精）"
    chart.y_axis.title = "组合"
    chart.x_axis.title = "胡数"
    chart.legend.position = "b"
    data = Reference(ws, min_col=5, min_row=3, max_col=6, max_row=9)  # 非主精+主精
    cats = Reference(ws, min_col=1, min_row=4, max_row=9)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    chart.height = 8.5
    chart.width = 18
    ws.add_chart(chart, "I3")


def build_black_sheet(wb):
    """Sheet2：黑精穿/泛 + 非精字面基础胡"""
    ws = wb.create_sheet("黑精穿泛牌")

    ws.merge_cells("A1:F1")
    c = ws["A1"]
    c.value = "黑精（乙/九）穿牌 / 泛牌查表"
    c.font = __import__("openpyxl").styles.Font(name=FONT, size=14, bold=True, color="C00000")
    c.alignment = __import__("openpyxl").styles.Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 26

    ws.merge_cells("A2:F2")
    c = ws["A2"]
    c.value = "黑精无赖子组合（赖子不能通配乙/九），穿牌为 5 张纯物理牌"
    c.font = __import__("openpyxl").styles.Font(name=FONT, size=10, italic=True, color="808080")
    c.alignment = __import__("openpyxl").styles.Alignment(horizontal="center", vertical="center")

    headers = ["组合", "皮数", "花数", "胡数", "JS key（花_皮_赖）"]
    for j, h in enumerate(headers, 1):
        _style_header(ws.cell(row=3, column=j, value=h))
    ws.row_dimensions[3].height = 22

    _style_cell(ws.cell(row=4, column=1, value="3皮2花"))
    _style_cell(ws.cell(row=4, column=2, value=3))
    _style_cell(ws.cell(row=4, column=3, value=2))
    _style_cell(ws.cell(row=4, column=4, value=6))
    _style_cell(ws.cell(row=4, column=5, value="2_3_0"))
    ws.row_dimensions[4].height = 20
    # 黑精不能当主精，恒按非主精计胡
    ws.merge_cells("A6:E6")
    c = ws["A6"]
    c.value = "注：黑精（乙/九）不能作为主精（游戏规则限制），恒按非主精计胡，无主精翻倍。"
    c.font = __import__("openpyxl").styles.Font(name=FONT, size=9, color="C00000")
    c.alignment = __import__("openpyxl").styles.Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[6].height = 16

    # 非精字面基础胡
    ws.merge_cells("A8:E8")
    c = ws["A8"]
    c.value = "非精字面穿牌（无精牌加成）"
    c.font = __import__("openpyxl").styles.Font(name=FONT, size=12, bold=True)
    _style_header(ws.cell(row=9, column=1, value="字面颜色"))
    _style_header(ws.cell(row=9, column=2, value="胡数"))
    _style_cell(ws.cell(row=10, column=1, value="红字面"))
    _style_cell(ws.cell(row=10, column=2, value=8))
    _style_cell(ws.cell(row=11, column=1, value="黑字面"))
    _style_cell(ws.cell(row=11, column=2, value=4))

    for col, w in zip("ABCDEF", [14, 8, 8, 10, 10, 20]):
        ws.column_dimensions[col].width = w


def build_note_sheet(wb):
    """Sheet3：适用范围、代码位置、历史坑"""
    ws = wb.create_sheet("说明")
    from openpyxl.styles import Font, Alignment, PatternFill
    ws.column_dimensions["A"].width = 6
    ws.column_dimensions["B"].width = 90

    rows = [
        ("适用范围", [
            "穿牌 = 泛牌（共用一张表，胡数相同）",
            "5 张同字（含赖子通配）",
            "主精 = 非主精 × 2（红精、黑精均成立）",
            "每种精牌最多 3皮 + 2花；赖子全局最多 2 张",
            "赖子只能通配三/五/七（红精），不能配乙/九（黑精）",
        ]),
        ("代码位置", [
            "JS 红精表：JING_RED_TABLE['chuan']（step5-hu.html）",
            "JS 黑精表：JING_BLACK_TABLE['chuan']（step5-hu.html）",
            "Python 红精表：_RED_JING_CHUAN_TABLE（计分引擎v3.py）",
            "Python 黑精表：_BLACK_JING_CHUAN_TABLE（计分引擎v3.py）",
            "校验：test_hu_tables_complete.js（含穿/泛全部组合）、test_chuan_table.js",
        ]),
        ("历史坑", [
            "JS 表曾缺 0_3_2（3皮2赖），穿牌走兜底公式算成 30 胡（应 56 主精），2026-08-24 已补全",
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
    build_red_sheet(wb)
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
