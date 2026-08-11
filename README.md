#  业务直连规则

## 项目用途

将指定国内业务网站强制 `DIRECT` 直连，避免经过 VPN。适用于 Windows 上 KuaJingCloud 的“系统代理 + 规则模式”。

## 规则文件

规则保存在 [`my-direct.txt`](./my-direct.txt)。文件采用一行一个域名的纯域名格式，不包含协议、端口、路径、查询参数或片段。

KuaJingCloud 可直接订阅的 Raw URL：

```text
https://raw.githubusercontent.com/druo69122-debug/fantastic-parakeet/main/my-direct.txt
```

##  添加方式

设置  
→ 规则订阅  
→ 添加订阅  
→ URL 填 `my-direct.txt` 的 Raw URL  
→ 名称填写“业务网站直连”  
→ 预览  
→ 动作选择“直连”  
→ 确定添加

## 添加域名

可以直接把一个或多个完整网址交给辅助脚本。脚本只提取网址中的域名，自动转为小写、去重，并保留已有规则：

```powershell
python scripts/add_domains.py "https://admin.abc.com/order/123" "https://api.abc.com/v1/order" "https://erp.test.cn/#/home"
```

也可以先运行脚本，再逐行粘贴网址；粘贴完成后，在 Windows 中按 `Ctrl+Z`，再按回车结束输入：

```powershell
python scripts/add_domains.py
```

脚本会列出本次新增的域名、已经存在的域名、忽略的错误输入数量，以及更新后的规则总数。

## 维护原则

- 只加入明确要求直连的域名。
- 完整网址只提取其子域名，不自动扩大到主域名。
- 仅在明确要求整个主域名直连时，才加入主域名。
- 更新时保留所有已有规则，并自动去重。
