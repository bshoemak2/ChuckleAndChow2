import { useColorScheme } from 'react-native';

export function useThemeColor({ light, dark }, colorName) {
  const scheme = useColorScheme();
  return scheme === 'dark' ? dark || '#fff' : light || '#000';
}