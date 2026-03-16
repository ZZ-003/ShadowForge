'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';

export default function HomePage() {
  return (
    <main className="min-h-screen">
      {/* 英雄区域 */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        {/* 动态背景 */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyber-purple/20 rounded-full blur-3xl animate-float" />
          <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-cyber-blue/20 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }} />
        </div>

        {/* 主内容 */}
        <div className="relative z-50 text-center px-4 -mt-24">
          {/* Logo 区域 */}
          <motion.div
            className="mb-4"
            initial={{ opacity: 0, y: -30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="inline-flex items-center gap-3">
              <div className="w-14 h-14 bg-gradient-to-br from-cyber-blue to-cyber-purple rounded-lg flex items-center justify-center shadow-lg shadow-cyber-blue/30">
                <svg
                  className="w-10 h-10 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 2L2 7l10 5 10-5-10 5M2 17l10 5 10-5M12 22V2"
                  />
                </svg>
              </div>
              <h1 className="text-6xl md:text-7xl font-bold text-gradient drop-shadow-2xl">
                DeepTrace
              </h1>
            </div>
          </motion.div>

          {/* 标题 */}
          <motion.p
            className="text-2xl md:text-3xl font-semibold text-gradient mb-5"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            多模态敏感数据深度仿真引擎
          </motion.p>

          {/* 描述 */}
          <motion.p
            className="text-lg text-gray-500 max-w-2xl mx-auto mb-8 whitespace-nowrap"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            基于生成式 AI 的网络安全测试平台，模拟真实数据泄露场景，为安全团队提供高质量的测试数据
          </motion.p>

          {/* CTA 按钮 */}
          <motion.div
            className="flex flex-col sm:flex-row gap-4 justify-center mb-12"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            <Link
              href="/auth/login"
              className="group px-8 py-3 bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-semibold rounded-lg hover:from-emerald-600 hover:to-teal-600 transition-all shadow-lg shadow-emerald-500/30 flex items-center justify-center gap-2"
            >
              <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
              </svg>
              开始使用
            </Link>
            <Link
              href="/dashboard/demo"
              className="group px-8 py-3 bg-gradient-to-r from-slate-700 to-slate-600 text-gray-200 font-semibold rounded-lg hover:from-slate-600 hover:to-slate-500 transition-all border border-slate-500/50 flex items-center justify-center gap-2"
            >
              <svg className="w-5 h-5 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              查看演示
            </Link>
          </motion.div>

          {/* 特性展示 */}
          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {[
              {
                icon: (
                  <svg className="w-6 h-6 text-cyber-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                ),
                color: 'cyber-blue',
                title: '多模态生成',
                desc: '支持文本、图像、音频、视频等多种数据类型的仿真生成'
              },
              {
                icon: (
                  <svg className="w-6 h-6 text-cyber-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                ),
                color: 'cyber-purple',
                title: '安全合规',
                desc: '所有生成数据均为仿真数据，不包含真实敏感信息'
              },
              {
                icon: (
                  <svg className="w-6 h-6 text-cyber-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                ),
                color: 'cyber-green',
                title: '高性能',
                desc: '基于分布式任务队列，支持大规模并发数据生成'
              }
            ].map((feature, i) => (
              <motion.div
                key={feature.title}
                className="p-6 bg-cyber-dark/90 backdrop-blur-sm rounded-xl border border-cyber-blue/30"
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.2, duration: 0.6 }}
              >
                <div className={`w-12 h-12 bg-${feature.color}/20 rounded-lg flex items-center justify-center mb-4`}>
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-200 mb-2">{feature.title}</h3>
                <p className="text-gray-400">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
