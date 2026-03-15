'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { useAuthStore } from '@/lib/store/auth';

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  useEffect(() => {
    if (!isAuthenticated) {
      window.location.href = '/auth/login';
      return;
    }
  }, [isAuthenticated]);

  // 模拟模板数据（实际应该从API获取）
  const mockTemplates = [
    {
      id: 1,
      name: 'VS Code API Key Leak',
      description: 'Simulates an API key leak in VS Code environment',
      category: 'IDE',
      modality: 'image',
      createdAt: '2026-03-14T12:00:00Z',
      thumbnail: '/api/placeholder/300/200'
    },
    {
      id: 2,
      name: 'Terminal Password Exposure',
      description: 'Shows password exposure in terminal/command line',
      category: 'CLI',
      modality: 'image',
      createdAt: '2026-03-14T11:30:00Z',
      thumbnail: '/api/placeholder/300/200'
    },
    {
      id: 3,
      name: 'Chat Application Secret',
      description: 'Secret sharing in chat application interface',
      category: 'Chat',
      modality: 'image',
      createdAt: '2026-03-14T11:00:00Z',
      thumbnail: '/api/placeholder/300/200'
    },
    {
      id: 4,
      name: 'Config File Credentials',
      description: 'Credentials exposed in configuration files',
      category: 'Config',
      modality: 'image',
      createdAt: '2026-03-14T10:30:00Z',
      thumbnail: '/api/placeholder/300/200'
    }
  ];

  useEffect(() => {
    // 模拟API调用
    const loadTemplates = async () => {
      try {
        setLoading(true);
        // 在实际应用中，这里应该调用API获取模板
        // const response = await apiClient.get('/api/templates');
        // setTemplates(response.data);
        setTimeout(() => {
          setTemplates(mockTemplates);
          setError(null);
        }, 500);
      } catch (err) {
        console.error('Failed to load templates:', err);
        setError('Failed to load templates');
      } finally {
        setLoading(false);
      }
    };

    loadTemplates();
  }, []);

  if (loading) {
    return (
      <div className="cyber-card text-center py-12">
        <div className="animate-pulse">Loading templates...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="cyber-card text-center py-12">
        <div className="text-red-400 mb-4">{error}</div>
        <button 
          onClick={() => window.location.reload()}
          className="cyber-button"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex items-center justify-between"
      >
        <h1 className="text-2xl font-bold text-gradient">Template Library</h1>
        <Link href="/dashboard/tasks/new" className="cyber-button">
          Create New Task
        </Link>
      </motion.div>

      {templates.length === 0 ? (
        <div className="cyber-card text-center py-12">
          <div className="text-gray-400 mb-4">No templates available</div>
          <Link href="/dashboard/tasks/new" className="cyber-button">
            Create Your First Template
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {templates.map((template) => (
            <motion.div
              key={template.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
              className="cyber-card overflow-hidden"
            >
              <div className="relative">
                <img 
                  src={template.thumbnail} 
                  alt={template.name}
                  className="w-full h-48 object-cover"
                />
                <div className="absolute top-2 right-2 bg-cyber-blue/80 text-white text-xs px-2 py-1 rounded">
                  {template.modality.toUpperCase()}
                </div>
              </div>
              
              <div className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-white">{template.name}</h3>
                  <span className="bg-cyber-purple/20 text-cyber-purple text-xs px-2 py-1 rounded">
                    {template.category}
                  </span>
                </div>
                <p className="text-sm text-gray-400 mb-4">{template.description}</p>
                
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Created: {new Date(template.createdAt).toLocaleDateString()}</span>
                  <Link 
                    href={`/dashboard/tasks/new?template=${template.id}`}
                    className="cyber-button text-xs px-3 py-1"
                  >
                    Use Template
                  </Link>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}