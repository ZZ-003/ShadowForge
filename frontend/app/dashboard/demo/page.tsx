'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';

export default function DemoPage() {
  return (
    <div className="space-y-6 p-6">
      {/* 演示标题 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="cyber-card"
      >
        <h1 className="text-3xl font-bold mb-2">
          DeepTrace 演示
        </h1>
        <p className="text-gray-400">
          体验多模态敏感数据深度仿真引擎的强大功能
        </p>
      </motion.div>

      {/* 功能展示 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* 生成任务演示 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.4 }}
          className="cyber-card group"
        >
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="font-semibold mb-2 flex items-center gap-2">
                <span>⚡</span>
                生成任务
              </h3>
              <p className="text-sm text-gray-400">
                创建各种类型的敏感数据泄露场景
              </p>
            </div>
          </div>
          <div className="space-y-3">
            <div className="p-3 bg-cyber-dark/50 rounded-lg">
              <div className="flex justify-between text-sm">
                <span>API Key泄露场景</span>
                <span className="text-cyber-green">已完成</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2 mt-2">
                <div className="bg-cyber-green h-2 rounded-full" style={{ width: '100%' }}></div>
              </div>
            </div>
            <div className="p-3 bg-cyber-dark/50 rounded-lg">
              <div className="flex justify-between text-sm">
                <span>数据库凭证泄露</span>
                <span className="text-cyber-yellow">进行中</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2 mt-2">
                <div className="bg-cyber-yellow h-2 rounded-full" style={{ width: '65%' }}></div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* 多模态输出演示 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.4 }}
          className="cyber-card group"
        >
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="font-semibold mb-2 flex items-center gap-2">
                <span>🖼️</span>
                多模态输出
              </h3>
              <p className="text-sm text-gray-400">
                支持图片、视频、音频等多种格式
              </p>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 bg-cyber-dark/50 rounded-lg text-center">
              <div className="text-2xl mb-1">🖼️</div>
              <div className="text-xs">图片</div>
            </div>
            <div className="p-3 bg-cyber-dark/50 rounded-lg text-center">
              <div className="text-2xl mb-1">🎬</div>
              <div className="text-xs">视频</div>
            </div>
            <div className="p-3 bg-cyber-dark/50 rounded-lg text-center">
              <div className="text-2xl mb-1">🎵</div>
              <div className="text-xs">音频</div>
            </div>
            <div className="p-3 bg-cyber-dark/50 rounded-lg text-center">
              <div className="text-2xl mb-1">📄</div>
              <div className="text-xs">文档</div>
            </div>
          </div>
        </motion.div>

        {/* 场景模拟演示 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.4 }}
          className="cyber-card group"
        >
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="font-semibold mb-2 flex items-center gap-2">
                <span>💻</span>
                场景模拟
              </h3>
              <p className="text-sm text-gray-400">
                模拟真实泄露环境
              </p>
            </div>
          </div>
          <div className="space-y-2">
            <div className="p-2 bg-cyber-dark/50 rounded text-sm">IDE代码泄露</div>
            <div className="p-2 bg-cyber-dark/50 rounded text-sm">终端命令泄露</div>
            <div className="p-2 bg-cyber-dark/50 rounded text-sm">聊天记录泄露</div>
            <div className="p-2 bg-cyber-dark/50 rounded text-sm">配置文件泄露</div>
          </div>
        </motion.div>
      </div>

      {/* 操作按钮 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.6 }}
        className="cyber-card flex flex-col items-center justify-center py-12"
      >
        <h3 className="text-xl font-semibold mb-4">准备好开始使用了吗？</h3>
        <p className="text-gray-400 text-center mb-6 max-w-md">
          登录以解锁全部功能，创建您自己的敏感数据泄露场景
        </p>
        <div className="flex gap-4">
          <Link
            href="/auth/login"
            className="cyber-button px-8 py-3 font-semibold"
          >
            立即登录
          </Link>
          <Link
            href="/auth/register"
            className="px-8 py-3 border border-cyber-blue text-cyber-blue font-semibold rounded-lg hover:bg-cyber-blue/10 transition-colors"
          >
            注册账户
          </Link>
        </div>
      </motion.div>
    </div>
  );
}