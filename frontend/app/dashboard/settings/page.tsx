'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { useAuthStore } from '@/lib/store/auth';
import { getCurrentUser, logout } from '@/lib/api/auth';

export default function SettingsPage() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  useEffect(() => {
    if (!isAuthenticated) return;

    const loadUser = async () => {
      try {
        setLoading(true);
        const userData = await getCurrentUser();
        setUser(userData);
        setError(null);
      } catch (err) {
        console.error('Failed to load user:', err);
        setError('Failed to load user information');
      } finally {
        setLoading(false);
      }
    };

    loadUser();
  }, [isAuthenticated]);

  const handleLogout = async () => {
    try {
      await logout();
      // Redirect to home page after logout
      window.location.href = '/';
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  if (loading) {
    return (
      <div className="cyber-card text-center py-12">
        <div className="animate-pulse">Loading settings...</div>
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
      >
        <h1 className="text-2xl font-bold text-gradient mb-6">System Settings</h1>
        
        {/* User Profile Section */}
        <div className="cyber-card p-6">
          <h2 className="text-xl font-semibold mb-4 text-white">User Profile</h2>
          
          {user && (
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 bg-gradient-to-br from-cyber-blue to-cyber-purple rounded-full flex items-center justify-center">
                  <span className="text-white font-bold text-lg">
                    {user.username.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div>
                  <h3 className="text-lg font-medium text-white">{user.username}</h3>
                  <p className="text-gray-400">{user.email}</p>
                  <p className="text-sm text-gray-500">
                    Member since: {new Date(user.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
              
              <div className="pt-4 border-t border-cyber-blue/20">
                <button 
                  onClick={handleLogout}
                  className="cyber-button bg-red-600 hover:bg-red-700"
                >
                  Logout
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Application Settings Section */}
        <div className="cyber-card p-6">
          <h2 className="text-xl font-semibold mb-4 text-white">Application Settings</h2>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium text-white">Dark Mode</h3>
                <p className="text-sm text-gray-400">Enable dark theme for the application</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" defaultChecked />
                <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-cyber-blue/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-cyber-blue"></div>
              </label>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium text-white">Auto-save</h3>
                <p className="text-sm text-gray-400">Automatically save your work periodically</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" defaultChecked />
                <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-cyber-blue/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-cyber-blue"></div>
              </label>
            </div>
          </div>
        </div>

        {/* Documentation Link */}
        <div className="cyber-card p-6">
          <h2 className="text-xl font-semibold mb-4 text-white">Documentation</h2>
          <p className="text-gray-400 mb-4">
            Learn more about DeepTrace features and how to use them effectively.
          </p>
          <Link href="/docs" className="cyber-button">
            View Documentation
          </Link>
        </div>
      </motion.div>
    </div>
  );
}