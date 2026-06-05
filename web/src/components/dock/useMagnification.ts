import { useLayoutEffect, useState, type RefObject } from 'react';
import { useSpring, useTransform, type MotionValue } from 'framer-motion';

export function useMagnification(ref: RefObject<HTMLElement>, mouseX: MotionValue<number>) {
  const [center, setCenter] = useState(-1000);

  useLayoutEffect(() => {
    function measure() {
      const node = ref.current;
      if (!node) {
        return;
      }
      const rect = node.getBoundingClientRect();
      setCenter(rect.left + rect.width / 2);
    }

    measure();
    window.addEventListener('resize', measure);
    window.addEventListener('scroll', measure, true);
    return () => {
      window.removeEventListener('resize', measure);
      window.removeEventListener('scroll', measure, true);
    };
  }, [ref]);

  const rawScale = useTransform(
    mouseX, 
    [center - 200, center - 120, center - 60, center, center + 60, center + 120, center + 200], 
    [1, 1.15, 1.45, 1.65, 1.45, 1.15, 1]
  );
  const scale = useSpring(rawScale, { stiffness: 450, damping: 36, mass: 0.5 });
  
  // Animate width to push neighbors - synchronized with the smoother scale
  const width = useTransform(scale, [1, 1.65], [62, 92]);
  const y = useTransform(scale, [1, 1.65], [0, -18]);
  const widthSpring = useSpring(width, { stiffness: 450, damping: 36, mass: 0.5 });

  return { scale, y, width: widthSpring };
}
