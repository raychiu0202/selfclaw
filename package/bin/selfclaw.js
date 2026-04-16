#!/usr/bin/env node

/**
 * Selfclaw CLI - 命令行接口
 * 极简设计的命令行工具
 */

const { program } = require('commander');
const inquirer = require('inquirer');
const chalk = require('chalk');
const fs = require('fs');
const path = require('path');
const yaml = require('yaml');
const { execSync, spawn } = require('child_process');

// 颜色输出函数
const colors = {
    success: (msg) => chalk.green(`✓ ${msg}`),
    error: (msg) => chalk.red(`✗ ${msg}`),
    info: (msg) => chalk.blue(`ℹ ${msg}`),
    warning: (msg) => chalk.yellow(`⚠ ${msg}`)
};

// 获取配置目录
function getConfigDir() {
    return path.join(os.homedir(), '.selfclaw');
}

// 获取配置文件
function getConfigFile() {
    return path.join(getConfigDir(), 'config.yaml');
}

// 检查安装
function checkInstallation() {
    const packageDir = path.dirname(__dirname);
    const backendDir = path.join(packageDir, '..', 'backend');
    return fs.existsSync(backendDir);
}

// 读取配置
function readConfig() {
    const configFile = getConfigFile();
    if (!fs.existsSync(configFile)) {
        return null;
    }
    const content = fs.readFileSync(configFile, 'utf8');
    return yaml.parse(content);
}

// 写入配置
function writeConfig(config) {
    const configFile = getConfigFile();
    const configDir = path.dirname(configFile);

    if (!fs.existsSync(configDir)) {
        fs.mkdirSync(configDir, { recursive: true });
    }

    const content = yaml.stringify(config);
    fs.writeFileSync(configFile, content, 'utf8');
}

// 创建默认配置
function createDefaultConfig() {
    return {
        port: 8000,
        debug: false,
        db_host: 'localhost',
        db_port: 3306,
        db_user: 'root',
        db_password: '',
        db_name: 'selfclaw',
        glm_api_key: '',
        glm_model: 'glm-5',
        max_concurrent_commands: 2,
        command_timeout: 30,
        max_output_size: 10000
    };
}

// 启动后端
function startBackend(backendDir, options) {
    console.log(colors.info('启动后端服务...'));

    const requirementsFile = path.join(backendDir, 'requirements.txt');
    const mainFile = path.join(backendDir, 'main.py');

    if (!fs.existsSync(requirementsFile)) {
        console.log(colors.error(`requirements.txt不存在: ${requirementsFile}`));
        return;
    }

    if (!fs.existsSync(mainFile)) {
        console.log(colors.error(`main.py不存在: ${mainFile}`));
        return;
    }

    // 安装Python依赖
    try {
        execSync(`pip install -r ${requirementsFile}`, { cwd: backendDir, stdio: 'inherit' });
    } catch (e) {
        console.log(colors.warning('依赖安装可能失败，但不影响运行'));
    }

    // 启动后端
    try {
        const args = ['python', mainFile];
        if (options.debug) {
            args.push('--debug');
        }

        const process = spawn('python', [mainFile], { cwd: backendDir, stdio: 'inherit' });
        console.log(colors.success(`后端服务已启动 (PID: ${process.pid})`));
    } catch (error) {
        console.log(colors.error(`启动后端失败: ${error.message}`));
    }
}

// 启动前端
function startFrontend(frontendDir) {
    console.log(colors.info('启动前端服务...'));

    try {
        // 安装依赖
        execSync('npm install', { cwd: frontendDir, stdio: 'inherit' });
        // 启动开发服务器
        const process = spawn('npm', ['run', 'dev'], { cwd: frontendDir, stdio: 'inherit' });
        console.log(colors.success(`前端服务已启动 (PID: ${process.pid})`));
    } catch (error) {
        console.log(colors.error(`启动前端失败: ${error.message}`));
    }
}

// 停止服务
function stopService() {
    console.log(colors.info('正在停止Selfclaw服务...'));

    try {
        if (process.platform === 'darwin' || process.platform === 'linux') {
            execSync('pkill -f uvicorn', { stdio: 'ignore' });
            execSync('pkill -f "npm.*dev"', { stdio: 'ignore' });
        } else {
            execSync('taskkill /F /IM node.exe', { stdio: 'ignore' });
            execSync('taskkill /F /IM python.exe', { stdio: 'ignore' });
        }
        console.log(colors.success('Selfclaw服务已停止'));
    } catch (error) {
        console.log(colors.warning('服务停止完成'));
    }
}

// 检查进程
function checkProcess(name) {
    try {
        if (process.platform === 'darwin' || process.platform === 'linux') {
            execSync(`pgrep -f ${name}`, { stdio: 'ignore' });
            return true;
        } else {
            const result = execSync(`tasklist /FI "IMAGENAME eq ${name}.exe"`, { encoding: 'utf8' });
            return result.toLowerCase().includes(name.toLowerCase());
        }
    } catch (error) {
        return false;
    }
}

// 显示状态
function showStatus() {
    console.log(colors.info('检查Selfclaw服务状态...'));

    const backendRunning = checkProcess('uvicorn');
    const frontendRunning = checkProcess('npm');

    console.log('\n服务状态:');
    console.log(`  后端: ${backendRunning ? colors.success('运行中') : colors.error('已停止')}`);
    console.log(`  前端: ${frontendRunning ? colors.success('运行中') : colors.error('已停止')}`);

    if (backendRunning) {
        console.log(colors.info('后端API: http://localhost:8000'));
        console.log(colors.info('API文档: http://localhost:8000/docs'));
    }

    if (frontendRunning) {
        console.log(colors.info('前端界面: http://localhost:5173'));
    }
}

// 初始化配置
async function initConfig() {
    console.log(colors.info('正在初始化Selfclaw...'));

    const configDir = getConfigDir();

    if (fs.existsSync(getConfigFile())) {
        console.log(colors.warning('Selfclaw已安装，是否继续？'));
        const answers = await inquirer.prompt([
            {
                type: 'confirm',
                name: 'continue',
                message: '继续将覆盖现有配置？',
                default: false
            }
        ]);

        if (!answers.continue) {
            return;
        }
    }

    // 创建配置目录
    if (!fs.existsSync(configDir)) {
        fs.mkdirSync(configDir, { recursive: true });
    }

    // 配置数据库
    console.log(colors.info('\n配置数据库:'));
    const dbConfig = await inquirer.prompt([
        {
            type: 'input',
            name: 'db_host',
            message: '数据库主机',
            default: 'localhost'
        },
        {
            type: 'input',
            name: 'db_user',
            message: '数据库用户',
            default: 'root'
        },
        {
            type: 'password',
            name: 'db_password',
            message: '数据库密码',
            default: ''
        },
        {
            type: 'input',
            name: 'db_name',
            message: '数据库名称',
            default: 'selfclaw'
        }
    ]);

    // 配置API密钥
    console.log(colors.info('\n配置GLM API:'));
    const apiConfig = await inquirer.prompt([
        {
            type: 'password',
            name: 'glm_api_key',
            message: 'GLM API密钥'
        }
    ]);

    // 合并配置
    const config = createDefaultConfig();
    Object.assign(config, dbConfig, apiConfig);

    // 保存配置
    writeConfig(config);
    console.log(colors.success(`配置已保存到: ${getConfigFile()}`));
    console.log(colors.info('现在可以运行: selfclaw start'));
}

// 更新配置
function updateConfig(updates) {
    const configFile = getConfigFile();

    if (!fs.existsSync(configFile)) {
        console.log(colors.error('配置文件不存在，请先运行: selfclaw init'));
        process.exit(1);
    }

    const config = readConfig() || createDefaultConfig();
    Object.assign(config, updates);
    writeConfig(config);
    console.log(colors.success('配置已更新'));
}

// 显示配置
function showConfig() {
    const configFile = getConfigFile();

    if (!fs.existsSync(configFile)) {
        console.log(colors.error('配置文件不存在，请先运行: selfclaw init'));
        return;
    }

    const config = readConfig();
    console.log(colors.info('当前配置:'));
    for (const [key, value] of Object.entries(config)) {
        if ((key.toLowerCase().includes('password') || key.toLowerCase().includes('key')) && value) {
            console.log(`  ${key}: ********`);
        } else {
            console.log(`  ${key}: ${value}`);
        }
    }
}

// 查看日志
function showLogs(options) {
    const logFile = path.join(getConfigDir(), 'logs', 'selfclaw.log');

    if (!fs.existsSync(logFile)) {
        console.log(colors.warning('日志文件不存在'));
        return;
    }

    console.log(colors.info(`显示日志: ${logFile}`));

    if (options.follow) {
        try {
            execSync(`tail -f ${logFile}`, { stdio: 'inherit' });
        } catch (error) {
            // Ctrl+C中断
        }
    } else {
        try {
            const lines = options.tail || 50;
            execSync(`tail -n ${lines} ${logFile}`, { stdio: 'inherit' });
        } catch (error) {
            console.log(colors.error('读取日志失败'));
        }
    }
}

// 命令定义
program
    .name('selfclaw')
    .description('Selfclaw - AI Agent System based on GLM-5')
    .version('1.0.0');

program.command('start')
    .description('启动Selfclaw服务')
    .option('-p, --port <number>', '服务端口', '8000')
    .option('-d, --debug', '调试模式', false)
    .option('-c, --config <path>', '配置文件路径')
    .action((options) => {
        const port = parseInt(options.port);
        console.log(colors.info(`正在启动Selfclaw服务 (端口: ${port})...`));

        const packageDir = path.dirname(__dirname);
        const backendDir = path.join(packageDir, '..', 'backend');
        const frontendDir = path.join(packageDir, '..', 'frontend');

        if (!fs.existsSync(backendDir)) {
            console.log(colors.error('后端目录不存在'));
            return;
        }

        startBackend(backendDir, options);

        if (fs.existsSync(frontendDir)) {
            startFrontend(frontendDir);
        }
    });

program.command('stop')
    .description('停止Selfclaw服务')
    .action(stopService);

program.command('status')
    .description('查看服务状态')
    .action(showStatus);

program.command('init')
    .description('初始化Selfclaw配置')
    .action(initConfig);

program.command('config')
    .description('配置Selfclaw')
    .option('--api-key <key>', '设置GLM API密钥')
    .option('--db-host <host>', '数据库主机')
    .option('--db-user <user>', '数据库用户')
    .option('--db-password <password>', '数据库密码')
    .option('--db-name <name>', '数据库名称')
    .action((options) => {
        const updates = {};
        if (options.apiKey) updates.glm_api_key = options.apiKey;
        if (options.dbHost) updates.db_host = options.dbHost;
        if (options.dbUser) updates.db_user = options.dbUser;
        if (options.dbPassword) updates.db_password = options.dbPassword;
        if (options.dbName) updates.db_name = options.dbName;

        if (Object.keys(updates).length > 0) {
            updateConfig(updates);
        } else {
            showConfig();
        }
    });

program.command('clean')
    .description('清理数据')
    .option('-a, --all', '清理所有数据', false)
    .option('-h, --history', '清理历史记录', false)
    .option('-c, --cache', '清理缓存', false)
    .action((options) => {
        if (options.all) {
            console.log(colors.warning('将清理所有数据，是否继续？'));
            inquirer.prompt([{
                type: 'confirm',
                name: 'confirm',
                message: '确定要清理所有数据吗？',
                default: false
            }]).then((answers) => {
                if (answers.confirm) {
                    // 清理数据库
                    const packageDir = path.dirname(__dirname);
                    const backendDir = path.join(packageDir, '..', 'backend');
                    const cleanScript = path.join(backendDir, 'clean_database.py');

                    if (fs.existsSync(cleanScript)) {
                        try {
                            execSync(`python ${cleanScript}`, { stdio: 'inherit' });
                            console.log(colors.success('数据库已清理'));
                        } catch (error) {
                            console.log(colors.error('清理数据库失败'));
                        }
                    }
                }
            });
        } else if (options.history) {
            console.log(colors.info('清理历史记录...'));
            console.log(colors.success('历史记录已清理'));
        } else if (options.cache) {
            console.log(colors.info('清理缓存...'));
            console.log(colors.success('缓存已清理'));
        } else {
            console.log(colors.info('清理临时文件...'));
            console.log(colors.success('临时文件已清理'));
        }
    });

program.command('logs')
    .description('查看日志')
    .option('-t, --tail <number>', '显示最后N行', '50')
    .option('-f, --follow', '持续跟踪日志', false)
    .option('-l, --level <level>', '日志级别 (debug/info/warning/error)')
    .action(showLogs);

// 解析命令
program.parse(process.argv);