import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { toast } from 'sonner';
import { RootState } from '../../../store';
import { removeNotification } from '../../../store/slices/notificationSlice';

export function EmployeeNotificationPanel() {
  const dispatch = useDispatch();
  const notifications = useSelector((state: RootState) => state.notifications.notifications);

  useEffect(() => {
    notifications.forEach((notification) => {
      switch (notification.type) {
        case 'success':
          toast.success(notification.message);
          break;
        case 'error':
          toast.error(notification.message);
          break;
        case 'warning':
          toast.warning(notification.message);
          break;
        case 'info':
        default:
          toast.info(notification.message);
          break;
      }
      // Clean up after showing
      dispatch(removeNotification(notification.id));
    });
  }, [notifications, dispatch]);

  return null; // This component doesn't render any visible DOM on its own
}
