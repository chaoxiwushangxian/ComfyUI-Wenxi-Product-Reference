# 文系商品参考图

这是一个 ComfyUI 文本节点。它读取参考图编号和提示词中的角色说明，给被指定为商品的图片补充外形、包装、标签和颜色的一致性要求。它支持普通中文提示词和分段的 H3 提示词。

## 安装

把整个仓库放在 `ComfyUI/custom_nodes/ComfyUI-Wenxi-Product-Reference/`，确保该目录直接包含 `__init__.py`。节点只用 Python 标准库。下次启动 ComfyUI 后，在 `Wenxi` 分类中搜索「文系商品参考图」。在托管环境中，运行工作流的实例也需要安装节点。

## 接线

| 端口 | 类型 | 内容 |
| --- | --- | --- |
| `prompt` | STRING 输入 | 原始提示词 |
| `slots` | STRING 输入 | 按第 1 至 9 张图的顺序，用竖线分隔九个空位标记。沿用工作流的约定，`False` 表示已提供图片，`True` 表示空位 |
| `prompt` | STRING 输出 | 处理后的完整提示词 |

例如，给 `prompt` 输入「图片1是商品。图片2是人物。」，给 `slots` 输入 `False|False|True|True|True|True|True|True|True`。输出会保留原文并追加图片 1 的商品保真要求。没有识别到有效商品图时，输出原文。

工作流可以在节点外控制清晰度和是否启用增强。节点类型标识为 `WenxiProductReferencePrompt`。

