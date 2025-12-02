# WSL 便捷执行脚本
# 用法: .\run-wsl.ps1 <command>

param(
    [Parameter(Mandatory=$false)]
    [string]$Command = "bash"
)

$ProjectPath = "/mnt/c/Users/HP/Desktop/MediaCrawer/MediaCrawer_Pro"

if ($Command -eq "test") {
    # 测试签名算法
    wsl bash -c "cd $ProjectPath/signature-service && node test_xhs_sign.js"
}
elseif ($Command -eq "start") {
    # 启动签名服务
    wsl bash -c "cd $ProjectPath/signature-service && npm start"
}
elseif ($Command -eq "install") {
    # 安装依赖
    wsl bash -c "cd $ProjectPath/signature-service && npm install"
}
elseif ($Command -eq "backend") {
    # 启动后端
    wsl bash -c "cd $ProjectPath/backend && python main.py"
}
elseif ($Command -eq "bash") {
    # 进入 WSL bash
    wsl bash -c "cd $ProjectPath && bash"
}
else {
    # 自定义命令
    wsl bash -c "cd $ProjectPath && $Command"
}





















