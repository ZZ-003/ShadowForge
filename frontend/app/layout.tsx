import type { Metadata } from 'next'
import { Inter, Fira_Code } from 'next/font/google'
import '../styles/globals.css'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
})

const firaCode = Fira_Code({
  subsets: ['latin'],
  variable: '--font-fira-code',
})

export const metadata: Metadata = {
  title: 'DeepTrace - 多模态敏感数据深度仿真引擎',
  description: '生成包含敏感信息的多模态泄露场景，用于安全测试、数据集构建和演示',
  keywords: ['网络安全', '数据泄露', '多模态生成', '安全测试', 'AI安全'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN" className={`${inter.variable} ${firaCode.variable}`}>
      <head>
        <link rel="icon" href="/favicon.ico" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body className="min-h-screen bg-cyber-black text-gray-200">
        {/* 扫描线效果 */}
        <div className="scan-line" />

        {/* 数据流效果 */}
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/4 left-0 w-full h-1 data-stream" />
          <div className="absolute top-1/2 left-0 w-full h-1 data-stream" style={{ animationDelay: '5s' }} />
          <div className="absolute top-3/4 left-0 w-full h-1 data-stream" style={{ animationDelay: '10s' }} />
        </div>

        {/* 背景网格 */}
        <div className="fixed inset-0 bg-cyber-grid bg-[length:50px_50px] opacity-10 pointer-events-none" />

        {/* 径向渐变 */}
        <div className="fixed inset-0 bg-cyber-radial opacity-20 pointer-events-none" />

        <main className="relative z-10">
          {children}
        </main>

        {/* 全局通知区域 */}
        <div id="notification-portal" />
      </body>
    </html>
  )
}