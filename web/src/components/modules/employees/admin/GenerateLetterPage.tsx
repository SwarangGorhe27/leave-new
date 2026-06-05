import React from 'react';
import { GenerateLetterPage as AppGenerateLetterPage } from '../../../../app/pages/admin/employees/management/GenerateLetterPage';

interface GenerateLetterPageProps {
  onBack?: () => void;
}

// Thin wrapper to use the app-level GenerateLetterPage so the module is dynamic
export function GenerateLetterPage(_props: GenerateLetterPageProps) {
  return <AppGenerateLetterPage />;
}
