import { useCommandPalette } from '@hooks/useCommandPalette';
import { useTheme } from '@hooks/useTheme';
import { AppShell } from '@components/layout/AppShell';
import { AIAssistant } from '@components/ui/AIAssistant';
import { CommandPalette, ToastViewport } from '@components/ui';

export default function App() {
  useTheme();
  useCommandPalette();

  return (
    <>
      <AppShell />
      <CommandPalette />
      <AIAssistant />
      <ToastViewport />
    </>
  );
}
