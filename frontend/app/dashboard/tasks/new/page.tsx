'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { createTask, createTasksBatch, TaskModality, TaskScene, BatchTaskResponse, BatchTaskResult } from '@/lib/api/tasks';

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
  { value: TaskScene.IDE, label: 'IDE 代码编辑器', icon: '💻' },
  { value: TaskScene.CLI, label: 'CLI 终端', icon: '⌨️' },
  { value: TaskScene.CHAT, label: '团队聊天', icon: '💬' },
  { value: TaskScene.CONFIG, label: '配置文件', icon: '⚙️' },
  { value: TaskScene.UI, label: 'UI 仪表板', icon: '📊' },
];

export default function NewTaskPage() {
  const router = useRouter();
  const [mode, setMode] = useState<'single' | 'batch'>('single');
  
  // 单条模式表单数据
  const [singleFormData, setSingleFormData] = useState({
    name: '',
    description: '',
    secret: '',
    secret_type: SECRET_TYPES[0],
    modality: TaskModality.IMAGE,
    scene: undefined as TaskScene | undefined,
  });

  // 批量模式表单数据
  const [batchFormData, setBatchFormData] = useState({
    name_prefix: '任务 - ',
    secrets: '',
    common_secret_type: SECRET_TYPES[0],
    common_modality: TaskModality.IMAGE,
    common_scene: undefined as TaskScene | undefined,
    common_description: '',
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setErrorState] = useState('');
  const [batchResult, setBatchResult] = useState<BatchTaskResponse | null>(null);

  // 判断当前模态是否支持泄露场景
  const isSceneSupported = SCENE_SUPPORTED_MODALITIES.includes(singleFormData.modality);
  const isBatchSceneSupported = SCENE_SUPPORTED_MODALITIES.includes(batchFormData.common_modality);

  // 单条提交处理
  const handleSingleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorState('');
    setBatchResult(null);

    try {
      await createTask({
        name: singleFormData.name,
        description: singleFormData.description || undefined,
        secret: singleFormData.secret,
        secret_type: singleFormData.secret_type,
        modality: singleFormData.modality,
        scene: singleFormData.scene,
      });

      // 跳转到任务列表
      router.push('/dashboard/tasks');
    } catch (error: any) {
      setErrorState(error.message || '创建任务失败');
    } finally {
      setIsLoading(false);
    }
  };

  // 批量提交处理
  const handleBatchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorState('');
    setBatchResult(null);

    // 解析秘密列表
    const secrets = batchFormData.secrets
      .split('\n')
      .map(s => s.trim())
      .filter(s => s.length > 0);

    if (secrets.length === 0) {
      setErrorState('请输入至少一个秘密');
      setIsLoading(false);
      return;
    }

    if (secrets.length > 100) {
      setErrorState('最多支持 100 个秘密');
      setIsLoading(false);
      return;
    }

    try {
      const response = await createTasksBatch({
        secrets,
        common_config: {
          name_prefix: batchFormData.name_prefix,
          secret_type: batchFormData.common_secret_type,
          modality: batchFormData.common_modality,
          scene: batchFormData.common_scene,
          description: batchFormData.common_description || undefined,
        },
      });

      setBatchResult(response);
      
      // 如果有成功创建的任务，可以选择跳转或继续
      if (response.success_count > 0 && response.failed_count === 0) {
        setTimeout(() => {
          router.push('/dashboard/tasks');
        }, 2000);
      }
    } catch (error: any) {
      setErrorState(error.message || '批量创建任务失败');
    } finally {
      setIsLoading(false);
    }
  };

  // 输入变化处理（单条）
  const handleSingleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setSingleFormData({
      ...singleFormData,
      [e.target.name]: e.target.value,
    });
  };

  // 输入变化处理（批量）
  const handleBatchInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setBatchFormData({
      ...batchFormData,
      [e.target.name]: e.target.value,
    });
  };

  // 切换模态（单条）
  const handleSingleModalityChange = (modality: TaskModality) => {
    if (!SCENE_SUPPORTED_MODALITIES.includes(modality)) {
      setSingleFormData({ ...singleFormData, modality, scene: undefined });
    } else {
      setSingleFormData({ ...singleFormData, modality });
    }
  };

  // 切换模态（批量）
  const handleBatchModalityChange = (modality: TaskModality) => {
    if (!SCENE_SUPPORTED_MODALITIES.includes(modality)) {
      setBatchFormData({ ...batchFormData, common_modality: modality, common_scene: undefined });
    } else {
      setBatchFormData({ ...batchFormData, common_modality: modality });
    }
  };

  // 渲染单条模式表单
  const renderSingleForm = () => (
    <>
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
              value={singleFormData.name}
              onChange={handleSingleInputChange}
              disabled={isLoading}
              className="cyber-input w-full"
              placeholder="例如：API Key 泄露场景"
            />
          </div>

          <div>
            <label htmlFor="description" className="block text-sm font-medium mb-2 text-gray-300">
              描述
            </label>
            <textarea
              id="description"
              name="description"
              value={singleFormData.description}
              onChange={handleSingleInputChange}
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
              value={singleFormData.secret_type}
              onChange={handleSingleInputChange}
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
              value={singleFormData.secret}
              onChange={handleSingleInputChange}
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
                  onClick={() => handleSingleModalityChange(modality.value)}
                  disabled={isLoading}
                  className={`p-4 rounded-lg border-2 transition-all text-center ${
                    singleFormData.modality === modality.value
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
                    onClick={() => setSingleFormData({ ...singleFormData, scene: scene.value })}
                    disabled={isLoading}
                    className={`p-3 rounded-lg border-2 transition-all text-center ${
                      singleFormData.scene === scene.value
                        ? 'border-cyber-blue bg-cyber-blue/20'
                        : 'border-cyber-blue/20 hover:border-cyber-blue hover:bg-cyber-blue/10'
                    }`}
                  >
                    <div className="text-xl mb-1">{scene.icon}</div>
                    <div className="text-xs font-medium">{scene.label}</div>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center p-6 text-gray-500">
              <p className="text-sm text-center">
                仅图片和视频支持场景选择
              </p>
            </div>
          )}
        </div>
      </div>
    </>
  );

  // 渲染批量模式表单
  const renderBatchForm = () => (
    <>
      {/* 批量设置 */}
      <div>
        <h2 className="text-lg font-semibold mb-4 text-cyber-blue">批量设置</h2>
        <div className="space-y-4">
          <div>
            <label htmlFor="name_prefix" className="block text-sm font-medium mb-2 text-gray-300">
              名称前缀
            </label>
            <input
              id="name_prefix"
              name="name_prefix"
              type="text"
              value={batchFormData.name_prefix}
              onChange={handleBatchInputChange}
              disabled={isLoading}
              className="cyber-input w-full"
              placeholder="例如：API Key 泄露 - "
            />
            <p className="text-xs text-gray-500 mt-1">
              生成的任务名称将自动添加序号，如：{batchFormData.name_prefix || '任务 - '}1、{batchFormData.name_prefix || '任务 - '}2...
            </p>
          </div>

          <div>
            <label htmlFor="common_description" className="block text-sm font-medium mb-2 text-gray-300">
              描述（可选）
            </label>
            <textarea
              id="common_description"
              name="common_description"
              value={batchFormData.common_description}
              onChange={handleBatchInputChange}
              disabled={isLoading}
              className="cyber-input w-full resize-none"
              rows={2}
              placeholder="所有任务的公共描述"
            />
          </div>

          <div>
            <label htmlFor="common_secret_type" className="block text-sm font-medium mb-2 text-gray-300">
              秘密类型 *
            </label>
            <select
              id="common_secret_type"
              name="common_secret_type"
              required
              value={batchFormData.common_secret_type}
              onChange={handleBatchInputChange}
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
        </div>
      </div>

      {/* 秘密列表 */}
      <div>
        <h2 className="text-lg font-semibold mb-4 text-cyber-blue">秘密列表</h2>
        <div>
          <label htmlFor="secrets" className="block text-sm font-medium mb-2 text-gray-300">
            秘密内容（每行一个）*
          </label>
          <textarea
            id="secrets"
            name="secrets"
            required
            value={batchFormData.secrets}
            onChange={handleBatchInputChange}
            disabled={isLoading}
            className="cyber-input w-full resize-none font-mono"
            rows={10}
            placeholder={`sk-proj-abc123...\nsk-proj-def456...\nsk-proj-ghi789...`}
          />
          <p className="text-xs text-gray-500 mt-1">
            每个秘密占一行，空行将被忽略。最多支持 100 个秘密。
          </p>
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
                  onClick={() => handleBatchModalityChange(modality.value)}
                  disabled={isLoading}
                  className={`p-4 rounded-lg border-2 transition-all text-center ${
                    batchFormData.common_modality === modality.value
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

          {isBatchSceneSupported ? (
            <div>
              <label className="block text-sm font-medium mb-3 text-gray-300">
                泄露场景（可选）
              </label>
              <div className="grid grid-cols-2 gap-3">
                {SCENES.map((scene) => (
                  <button
                    key={scene.value}
                    type="button"
                    onClick={() => setBatchFormData({ ...batchFormData, common_scene: scene.value })}
                    disabled={isLoading}
                    className={`p-3 rounded-lg border-2 transition-all text-center ${
                      batchFormData.common_scene === scene.value
                        ? 'border-cyber-blue bg-cyber-blue/20'
                        : 'border-cyber-blue/20 hover:border-cyber-blue hover:bg-cyber-blue/10'
                    }`}
                  >
                    <div className="text-xl mb-1">{scene.icon}</div>
                    <div className="text-xs font-medium">{scene.label}</div>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center p-6 text-gray-500">
              <p className="text-sm text-center">
                仅图片和视频支持场景选择
              </p>
            </div>
          )}
        </div>
      </div>
    </>
  );

  // 渲染批量操作结果
  const renderBatchResult = () => {
    if (!batchResult) return null;

    const successCount = batchResult.success_count;
    const failedCount = batchResult.failed_count;
    const totalItems = batchResult.results.length;

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="cyber-card space-y-4"
      >
        <h2 className="text-lg font-semibold text-cyber-blue">批量创建结果</h2>
        
        {/* 统计信息 */}
        <div className="grid grid-cols-3 gap-4">
          <div className="p-4 bg-green-500/20 border border-green-500/30 rounded-lg">
            <div className="text-2xl font-bold text-green-400">{successCount}</div>
            <div className="text-sm text-gray-400">成功</div>
          </div>
          <div className="p-4 bg-red-500/20 border border-red-500/30 rounded-lg">
            <div className="text-2xl font-bold text-red-400">{failedCount}</div>
            <div className="text-sm text-gray-400">失败</div>
          </div>
          <div className="p-4 bg-cyber-blue/20 border border-cyber-blue/30 rounded-lg">
            <div className="text-2xl font-bold text-cyber-blue">{totalItems}</div>
            <div className="text-sm text-gray-400">总计</div>
          </div>
        </div>

        {/* 失败详情 */}
        {failedCount > 0 && (
          <div className="space-y-2">
            <h3 className="font-medium text-red-400">失败详情：</h3>
            {batchResult.results.filter(r => !r.success).map((result, index) => (
              <div key={index} className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-sm">
                <span className="text-red-400">错误:</span> {result.error}
              </div>
            ))}
          </div>
        )}

        {/* 成功详情（折叠） */}
        {successCount > 0 && (
          <details className="group">
            <summary className="cursor-pointer p-3 bg-green-500/10 border border-green-500/20 rounded-lg text-sm text-green-400 group-open:text-green-300">
              查看成功详情 ({successCount})
            </summary>
            <div className="mt-2 space-y-2 max-h-64 overflow-y-auto">
              {batchResult.results.filter(r => r.success).map((result, index) => (
                <div key={index} className="p-3 bg-green-500/5 border border-green-500/10 rounded-lg text-sm">
                  <span className="text-green-400">✓</span> {result.task?.name} (ID: {result.task?.id})
                </div>
              ))}
            </div>
          </details>
        )}

        {/* 操作按钮 */}
        <div className="flex gap-3 pt-4">
          <Link
            href="/dashboard/tasks"
            className="cyber-button px-6 py-2 inline-flex items-center gap-2 bg-green-500/20 text-green-400 border border-green-500/30 hover:bg-green-500/30"
          >
            查看任务列表
          </Link>
          <button
            onClick={() => {
              setBatchResult(null);
              setBatchFormData({
                ...batchFormData,
                secrets: '',
              });
            }}
            className="cyber-button px-6 py-2 inline-flex items-center gap-2 bg-cyber-dark text-gray-300 border border-cyber-blue/20 hover:bg-cyber-blue/10"
          >
            继续创建
          </button>
        </div>
      </motion.div>
    );
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

      {/* 模式切换 */}
      <div className="cyber-card p-4">
        <div className="flex gap-4">
          <button
            type="button"
            onClick={() => {
              setMode('single');
              setBatchResult(null);
              setErrorState('');
            }}
            className={`px-6 py-3 rounded-lg font-medium transition-all ${
              mode === 'single'
                ? 'bg-cyber-blue text-cyber-black'
                : 'bg-cyber-dark text-gray-400 hover:text-gray-200'
            }`}
          >
            单条创建
          </button>
          <button
            type="button"
            onClick={() => {
              setMode('batch');
              setBatchResult(null);
              setErrorState('');
            }}
            className={`px-6 py-3 rounded-lg font-medium transition-all ${
              mode === 'batch'
                ? 'bg-cyber-blue text-cyber-black'
                : 'bg-cyber-dark text-gray-400 hover:text-gray-200'
            }`}
          >
            批量创建
          </button>
        </div>
      </div>

      {/* 批量操作结果 */}
      {batchResult && renderBatchResult()}

      {/* 表单 */}
      {!batchResult && (
        <motion.form
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          onSubmit={mode === 'single' ? handleSingleSubmit : handleBatchSubmit}
          className="cyber-card space-y-6"
        >
          {mode === 'single' ? renderSingleForm() : renderBatchForm()}

          {/* 提交按钮 */}
          <div className="flex gap-4 pt-4 border-t border-cyber-blue/20">
            <Link
              href="/dashboard/tasks"
              className="cyber-button px-6 py-3 inline-flex items-center gap-2 bg-cyber-dark text-gray-300 border border-cyber-blue/20 hover:bg-cyber-blue/10"
            >
              取消
            </Link>
            <button
              type="submit"
              disabled={isLoading}
              className="cyber-button px-6 py-3 inline-flex items-center gap-2 bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-semibold rounded-lg hover:from-emerald-600 hover:to-teal-600 transition-all shadow-lg shadow-emerald-500/30 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  {mode === 'single' ? '创建中...' : `批量创建 (${batchFormData.secrets.split('\n').filter(s => s.trim()).length} 个)...`}
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  {mode === 'single' ? '创建任务' : '批量创建'}
                </>
              )}
            </button>
          </div>
        </motion.form>
      )}
    </div>
  );
}
