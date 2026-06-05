import { Network } from 'lucide-react';
import { Select, type SelectOption } from '@components/ui';

interface MasterSelectProps {
  label: string;
  value?: string;
  onValueChange: (value: string) => void;
  options: SelectOption[];
  helperText?: string;
  error?: string;
  required?: boolean;
}

export function MasterSelect(props: MasterSelectProps) {
  return <Select {...props} leftIcon={<Network className="h-4 w-4" />} placeholder="Select master value" />;
}
