# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'SimSun', 'KaiTi', 'DengXian']
plt.rcParams['axes.unicode_minus'] = False

tree = {
    'label': '记忆归档', 'color': '#2c3e50', 'children': [
        {'label': '非花牌记忆', 'color': '#27ae60', 'children': [
            {'label': '01 用户偏好与身份'},
            {'label': '02 连接器配置'},
            {'label': '06 其他项目'}]},
        {'label': '花牌游戏项目分析', 'color': '#2980b9', 'children': [
            {'label': '核心文档', 'color': '#8e44ad', 'children': [
                {'label': 'README 项目分析'},
                {'label': '01 项目结构地图'},
                {'label': '02 核心游戏流程'},
                {'label': '05 调试定位与风险'}]},
            {'label': '规则与计胡', 'color': '#e67e22', 'children': [
                {'label': '03 规则引擎与计胡'},
                {'label': '精牌穿牌查表汇总'},
                {'label': '精牌坎牌扎牌招牌查表'}]},
            {'label': 'AI 决策系统', 'color': '#c0392b', 'children': [
                {'label': '04 AI决策 (Phase1~7.8)'},
                {'label': '06 Phase7.7 执行总结'}]},
            {'label': '界面与移动端', 'color': '#16a085', 'children': [
                {'label': '手机适配方案'}]}]},
        {'label': '花牌代码仓库', 'color': '#7f8c8d', 'children': [
            {'label': 'uploads 花牌游戏PWA'},
            {'label': 'huapai-game GitHub'},
            {'label': '在线版 step5-hu.html'}]},
    ]
}


def is_leaf(n):
    return 'children' not in n


def cnt(n):
    if is_leaf(n):
        return 1
    return sum(cnt(c) for c in n['children'])


# ---- 节点尺寸：按文字长度动态计算 ----
def box_size(label, depth):
    # 叶子按字符数自适应宽度
    nchar = len(label)
    if depth == 0:
        w, h, fs = 1.5, 0.5, 14
    elif nchar >= 14:
        w, h, fs = 3.0, 0.46, 9.5
    elif nchar >= 10:
        w, h, fs = 2.4, 0.42, 10.5
    elif nchar >= 7:
        w, h, fs = 1.9, 0.40, 11
    else:
        w, h, fs = 1.5, 0.38, 11.5
    return w, h, fs


pos = {}
size = {}


def lay(n, x, y_center, depth):
    lab = n['label']
    w, h, fs = box_size(lab, depth)
    kids = n.get('children', [])
    pos[lab] = (x, y_center)
    size[lab] = (w, h, fs)
    if kids:
        cy = y_center
        for ch in kids:
            cc = cnt(ch)
            lay(ch, x + 1.9, cy - (cc - 1) / 2.0, depth + 1)
            cy -= cc


lay(tree, 0, 0, 0)

# 画布范围：含所有节点的左右边界（x方向留足）
xs = [pos[k][0] for k in pos]
ys = [pos[k][1] for k in pos]
right_edges = [pos[k][0] + size[k][0] / 2 for k in pos]
left_edges = [pos[k][0] - size[k][0] / 2 for k in pos]
canvas_x = (min(left_edges) - 0.6, max(right_edges) + 0.6)
canvas_y = (min(ys) - 0.8, max(ys) + 0.8)

fig, ax = plt.subplots(figsize=(14, 8.8))
ax.set_xlim(canvas_x)
ax.set_ylim(canvas_y)
ax.axis('off')
ax.set_facecolor('white')


def draw(n, depth):
    lab = n['label']
    x, y = pos[lab]
    w, h, fs = size[lab]
    color = n.get('color', '#95a5a6')
    if not is_leaf(n):
        for ch in n['children']:
            clab = ch['label']
            cx, cyy = pos[clab]
            # 从父节点右边界到子节点左边界
            ax.plot([x + w / 2, cx - size[clab][0] / 2], [y, cyy],
                    color='#c0c0c0', lw=1.4, zorder=1)
            draw(ch, depth + 1)
    box = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                         boxstyle='round,pad=0.02', fc=color, ec='none', zorder=3)
    ax.add_patch(box)
    ax.text(x, y, lab, ha='center', va='center', fontsize=fs,
            color='white', fontweight='bold', zorder=4)


draw(tree, 0)

out = r"C:\Users\XBW\Documents\lingxi-claw\users\7022512\projects\11672630128672961\workspace\记忆归档\归档索引思维导图.png"
fig.savefig(out, dpi=170, facecolor='white')
plt.close(fig)
from PIL import Image
img = Image.open(out)
print('保存成功:', out, '尺寸:', img.size)
