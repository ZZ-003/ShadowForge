'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { createTask, TaskModality, TaskScene } from '@/lib/api/tasks';

const SECRET_TYPES = [
  'API Key',
  'JWT Secret',
  'Database URL',
  'AWS Access Key',
  'GitHub Token',
  'OpenAI API Key',
  'Password',
  'Client Secret',
  'Private Key',
  'Token',
];

const MODALITIES = [
  { value: TaskModality.IMAGE, label: '图片', icon: '🖼️' },
  { value: TaskModality.VIDEO, label: '视频', icon: '🎬' },
  { value: TaskModality.AUDIO, label: '音频', icon: '🎵' },
  { value: TaskModality.PDF, label: 'PDF', icon: '📄' },
  { value: TaskModality.WORD, label: 'Word', icon: '📝' },
  { value: TaskModality.PPT, label: 'PPT', icon: '📊' },
];

// 支持泄露场景的模态（image, video）
const SCENE_SUPPORTED_MODALITIES = [TaskModality.IMAGE, TaskModality.VIDEO];

const SCENES = [
  { value: TaskScene.IDE, label: 'IDE代码编辑器', icon: '💻' },
  { value: TaskScene.CLI, label: 'CLI终端', icon: '⌨️' },
  { value: TaskScene.CHAT, label: '团队聊天', icon: '💬' },
  { value: TaskScene.CONFIG, label: '配置文件', icon: '⚙️' },
  { value: TaskScene.UI, label: 'UI仪表板', icon: '📊' },
];

export default function NewTaskPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    secret: '',
    secret_type: SECRET_TYPES[0],
    modality: TaskModality.IMAGE,
    scene: undefined as TaskScene | undefined,
  });

  // 判断当前模态是否支持泄露场景
  const isSceneSupported = SCENE_SUPPORTED_MODALITIES.includes(formData.modality);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setErrorState] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorState('');

    try {
      await createTask({
        name: formData.name,
        description: formData.description || undefined,
        secret: formData.secret,
        secret_type: formData.secret_type,
        modality: formData.modality,
        scene: formData.scene,
      });

      // 跳转到任务列表
      router.push('/dashboard/tasks');
    } catch (error: any) {
      setErrorState(error.message || '创建任务失败');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* 标题 */}
      <div className="flex items-center gap-4">
        <Link
          href="/dashboard/tasks"
          className="p-2 rounded-lg hover:bg-cyber-blue/10 transition-colors"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </Link>
        <h1 className="text-3xl font-bold">创建新任务</h1>
      </div>

      {/* 错误提示 */}
      {error && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="p-4 bg-red-500/20 border border-red-500/30 rounded-lg text-red-400"
        >
          {error}
        </motion.div>
      )}

      {/* 表单 */}
      <motion.form
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        onSubmit={handleSubmit}
        className="cyber-card space-y-6"
      >
        {/* 基本信息 */}
        <div>
          <h2 className="text-lg font-semibold mb-4 text-cyber-blue">基本信息</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium mb-2 text-gray-300">
                任务名称 *
              </label>
              <input
                id="name"
                name="name"
                type="text"
                required
                value={formData.name}
                onChange={handleInputChange}
                disabled={isLoading}
                className="cyber-input w-full"
                placeholder="例如：API Key泄露场景"
              />
            </div>

            <div>
              <label htmlFor="description" className="block text-sm font-medium mb-2 text-gray-300">
                描述
              </label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                disabled={isLoading}
                className="cyber-input w-full resize-none"
                rows={3}
                placeholder="可选的描述信息"
              />
            </div>
          </div>
        </div>

        {/* 秘密信息 */}
        <div>
          <h2 className="text-lg font-semibold mb-4 text-cyber-blue">秘密信息</h2>
          <div className="space-y-4">
            <div>
              <label htmlFor="secret_type" className="block text-sm font-medium mb-2 text-gray-300">
                秘密类型 *
              </label>
              <select
                id="secret_type"
                name="secret_type"
                required
                value={formData.secret_type}
                onChange={handleInputChange}
                disabled={isLoading}
                className="cyber-input w-full"
              >
                {SECRET_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="secret" className="block text-sm font-medium mb-2 text-gray-300">
                秘密内容 *
              </label>
              <textarea
                id="secret"
                name="secret"
                required
                value={formData.secret}
                onChange={handleInputChange}
                disabled={isLoading}
                className="cyber-input w-full resize-none font-mono"
                rows={3}
                placeholder="例如：sk-proj-abc123..."
              />
            </div>
          </div>
        </div>

        {/* 输出设置 */}
        <div>
          <h2 className="text-lg font-semibold mb-4 text-cyber-blue">输出设置</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium mb-3 text-gray-300">
                输出模态 *
              </label>
              <div className="grid grid-cols-3 gap-3">
                {MODALITIES.map((modality) => (
                  <button
                    key={modality.value}
                    type="button"
                    onClick={() => {
                      // 切换模态时，如果不支持场景，则清除场景值
                      if (!SCENE_SUPPORTED_MODALITIES.includes(modality.value)) {
                        setFormData({ ...formData, modality: modality.value, scene: undefined });
                      } else {
                        setFormData({ ...formData, modality: modality.value });
                      }
                    }}
                    disabled={isLoading}
                    className={`p-4 rounded-lg border-2 transition-all text-center ${
                      formData.modality === modality.value
                        ? 'border-cyber-blue bg-cyber-blue/20'
                        : 'border-cyber-blue/20 hover:border-cyber-blue hover:bg-cyber-blue/10'
                    }`}
                  >
                    <div className="text-2xl mb-1">{modality.icon}</div>
                    <div className="text-sm font-medium">{modality.label}</div>
                  </button>
                ))}
              </div>
            </div>

            {isSceneSupported ? (
              <div>
                <label className="block text-sm font-medium mb-3 text-gray-300">
                  泄露场景（可选）
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {SCENES.map((scene) => (
                    <button
                      key={scene.value}
                      type="button"
                      onClick={() => setFormData({ ...formData, scene: scene.value })}
                      disabled={isLoading}
                      className={`p-4 rounded-lg border-2 transition-all text-center ${
                        formData.scene === scene.value
                          ? 'border-cyber-blue bg-cyber-blue/20'
                          : 'border-cyber-blue/20 hover:border-cyber-blue hover:bg-cyber-blue/10'
                      }`}
                    >
                      <div className="text-2xl mb-1">{scene.icon}</div>
                      <div className="text-sm font-medium">{scene.label}</div>
                    </button>
                  ))}
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  不选择时，LLM 会自动判断最适合的场景
                </p>
              </div>
            ) : (
              <div>
                <label className="block text-sm font-medium mb-3 text-gray-300">
                  泄露场景
                </label>
                <div className="p-4 rounded-lg border border-cyber-blue/20 bg-cyber-blue/5 text-gray-400 text-sm">
                  <div className="flex items-center gap-2">
                    <span className="text-xl">ℹ️</span>
                    <span>
                      {formData.modality === TaskModality.AUDIO && '音频模态无需指定泄露场景'}
                      {formData.modality === TaskModality.PDF && 'PDF 模态无需指定泄露场景'}
                      {formData.modality === TaskModality.WORD && 'Word 模态无需指定泄露场景'}
                      {formData.modality === TaskModality.PPT && 'PPT 模态无需指定泄露场景'}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 操作按钮 */}
        <div className="flex items-center justify-end gap-3 pt-4 border-t border-cyber-blue/20">
          <Link
            href="/dashboard/tasks"
            className="px-6 py-3 border border-cyber-blue/30 rounded-lg hover:bg-cyber-blue/10 transition-colors"
          >
            取消
          </Link>
          <button
            type="submit"
            disabled={isLoading}
            className="cyber-button px-8 py-3 font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <div className="flex items-center justify-center gap-2">
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>创建中...</span>
              </div>
            ) : (
              '创建任务'
            )}
          </button>
        </div>
      </motion.form>

      {/* 帮助提示 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.6 }}
        className="cyber-card"
      >
        <h3 className="font-semibold mb-3 flex items-center gap-2">
          <svg className="w-5 h-5 text-cyber-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          提示
        </h3>
        <ul className="space-y-2 text-sm text-gray-400">
          <li>• 秘密类型将帮助LLM生成更合适的内容</li>
          <li>• 选择与秘密类型最匹配的泄露场景</li>
          <li>• 视频模态会生成可滚动的长内容</li>
          <li>• 任务创建后可以在后台运行，无需等待</li>
        </ul>
      </motion.div>
    </div>
  );
}
