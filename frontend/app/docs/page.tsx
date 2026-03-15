'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';

export default function DocumentationPage() {
  const sections = [
    {
      title: 'Getting Started',
      description: 'Learn how to set up and start using DeepTrace',
      link: '#getting-started'
    },
    {
      title: 'Creating Tasks',
      description: 'How to create and configure data generation tasks',
      link: '#creating-tasks'
    },
    {
      title: 'Output Formats',
      description: 'Supported output formats and file types',
      link: '#output-formats'
    },
    {
      title: 'API Reference',
      description: 'Complete API documentation for developers',
      link: '#api-reference'
    },
    {
      title: 'Security Guidelines',
      description: 'Best practices for secure data handling',
      link: '#security-guidelines'
    },
    {
      title: 'Troubleshooting',
      description: 'Common issues and their solutions',
      link: '#troubleshooting'
    }
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center py-12"
      >
        <h1 className="text-4xl font-bold text-gradient mb-4">DeepTrace Documentation</h1>
        <p className="text-xl text-gray-400 max-w-2xl mx-auto">
          Comprehensive guide to using DeepTrace for generating realistic data leakage simulations
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {sections.map((section, index) => (
          <motion.div
            key={section.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            className="cyber-card p-6"
          >
            <h2 className="text-xl font-semibold text-white mb-3">{section.title}</h2>
            <p className="text-gray-400 mb-4">{section.description}</p>
            <Link 
              href={section.link}
              className="text-cyber-blue hover:text-cyber-purple transition-colors font-medium"
            >
              Read More →
            </Link>
          </motion.div>
        ))}
      </div>

      {/* Getting Started Section */}
      <motion.div
        id="getting-started"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.5 }}
        className="cyber-card p-8"
      >
        <h2 className="text-2xl font-bold text-white mb-6">Getting Started</h2>
        
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold text-white mb-3">1. Account Setup</h3>
            <p className="text-gray-400">
              Create an account or log in to access all DeepTrace features. Your account allows you to
              save templates, track task history, and manage your generated datasets.
            </p>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-white mb-3">2. Creating Your First Task</h3>
            <p className="text-gray-400 mb-4">
              Navigate to the "Generate Tasks" section and click "Create New Task". Fill in the required 
              information including:
            </p>
            <ul className="list-disc list-inside text-gray-400 space-y-2">
              <li><strong>Secret Type:</strong> Choose the type of sensitive data to simulate (API keys, passwords, etc.)</li>
              <li><strong>Modality:</strong> Select the output format (image, video, audio, PDF, etc.)</li>
              <li><strong>Scene:</strong> Choose the context where the data appears (IDE, terminal, chat, etc.)</li>
              <li><strong>Description:</strong> Provide details about your specific use case</li>
            </ul>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-white mb-3">3. Running and Monitoring Tasks</h3>
            <p className="text-gray-400">
              Once created, your task will appear in the task list. Click "Run" to start generation. 
              Monitor progress in real-time and download completed outputs from the "Output Files" section.
            </p>
          </div>
        </div>
      </motion.div>

      {/* Output Formats Section */}
      <motion.div
        id="output-formats"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.6 }}
        className="cyber-card p-8"
      >
        <h2 className="text-2xl font-bold text-white mb-6">Supported Output Formats</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[
            { name: 'Images', formats: ['PNG', 'JPG', 'GIF'], icon: '🖼️' },
            { name: 'Videos', formats: ['MP4', 'AVI', 'MOV'], icon: '🎥' },
            { name: 'Audio', formats: ['MP3', 'WAV', 'OGG'], icon: '🎵' },
            { name: 'Documents', formats: ['PDF'], icon: '📄' },
            { name: 'Word Docs', formats: ['DOCX'], icon: '📝' },
            { name: 'Presentations', formats: ['PPTX'], icon: '📊' }
          ].map((format) => (
            <div key={format.name} className="border border-cyber-blue/20 rounded-lg p-4">
              <div className="flex items-center gap-3 mb-3">
                <span className="text-2xl">{format.icon}</span>
                <h3 className="font-semibold text-white">{format.name}</h3>
              </div>
              <p className="text-sm text-gray-400">
                {format.formats.join(', ')}
              </p>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Security Guidelines Section */}
      <motion.div
        id="security-guidelines"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.7 }}
        className="cyber-card p-8"
      >
        <h2 className="text-2xl font-bold text-white mb-6">Security Guidelines</h2>
        
        <div className="space-y-4 text-gray-400">
          <p>
            <strong>Important:</strong> DeepTrace generates simulated data for training and testing purposes only.
            Never use real sensitive information as input to the system.
          </p>
          
          <p>
            All generated files are stored securely and can be downloaded or deleted at any time. 
            Regular cleanup of old outputs is recommended to maintain optimal storage usage.
          </p>
          
          <p>
            The system uses industry-standard encryption for data transmission and storage. 
            Your authentication tokens are stored securely in browser local storage with appropriate security measures.
          </p>
        </div>
      </motion.div>

      <div className="text-center py-8">
        <Link href="/dashboard" className="cyber-button">
          Back to Dashboard
        </Link>
      </div>
    </div>
  );
}