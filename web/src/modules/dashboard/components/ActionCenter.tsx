import { SectionContainer } from './kit/SectionContainer';
import { ActionList } from './kit/ActionList';
import type { DepartmentData } from './WorkforceDistribution';

interface ActionCenterProps {
  departments?: DepartmentData[];
  isLoading?: boolean;
}

export function ActionCenter({ departments, isLoading }: ActionCenterProps) {
  return (
    <SectionContainer
      title="Employees by Department"
      description="Workforce distribution overview"
    >
      <ActionList departments={departments} isLoading={isLoading} />
    </SectionContainer>
  );
}
