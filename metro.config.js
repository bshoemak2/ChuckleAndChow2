const { getDefaultConfig } = require('@expo/metro-config');

const defaultConfig = getDefaultConfig(__dirname);

module.exports = {
  ...defaultConfig,
  resolver: {
    ...defaultConfig.resolver,
    sourceExts: [...defaultConfig.resolver.sourceExts, 'tsx', 'ts', 'js'],
    alias: {
      '@/components': './components',
      '@/hooks': './hooks'
    }
  }
};