import { useEffect, useState, type RefObject } from "react";
import { createPortal } from "react-dom";
import { useNavigate } from "react-router";
import { LogOut, UserRoundCog } from "lucide-react";

type ProfileUserMenuProps = {
  open: boolean;
  onClose: () => void;
  anchorRef: RefObject<HTMLButtonElement | null>;
  profilePath: string;
  userName?: string;
  userEmail?: string;
  onLogout: () => void;
};

export function ProfileUserMenu({
  open,
  onClose,
  anchorRef,
  profilePath,
  userName,
  userEmail,
  onLogout,
}: ProfileUserMenuProps) {
  const navigate = useNavigate();
  const [position, setPosition] = useState({ top: 0, right: 16 });

  useEffect(() => {
    if (!open || !anchorRef.current) return;

    const updatePosition = () => {
      const rect = anchorRef.current!.getBoundingClientRect();
      setPosition({
        top: rect.bottom + 6,
        right: Math.max(8, window.innerWidth - rect.right),
      });
    };

    updatePosition();
    window.addEventListener("resize", updatePosition);
    window.addEventListener("scroll", updatePosition, true);
    return () => {
      window.removeEventListener("resize", updatePosition);
      window.removeEventListener("scroll", updatePosition, true);
    };
  }, [open, anchorRef]);

  useEffect(() => {
    if (!open) return;
    const onEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onEscape);
    return () => document.removeEventListener("keydown", onEscape);
  }, [open, onClose]);

  if (!open) return null;

  const handleProfile = () => {
    onClose();
    navigate(profilePath);
  };

  const handleSignOut = () => {
    onClose();
    onLogout();
  };

  return createPortal(
    <>
      <div
        className="profile-dropdown-backdrop fixed inset-0"
        role="presentation"
        onClick={onClose}
      />
      <div
        className="profile-dropdown-menu fixed w-48 border border-border rounded-lg shadow-lg overflow-hidden"
        style={{ top: position.top, right: position.right }}
        role="menu"
      >
        <div className="px-3 py-2.5 border-b border-border bg-card">
          <p className="text-[12px] font-semibold text-foreground">{userName}</p>
          {userEmail ? (
            <p className="text-[10px] text-muted-foreground mt-0.5 truncate">{userEmail}</p>
          ) : null}
        </div>
        <div className="p-1 bg-card">
          <button
            type="button"
            role="menuitem"
            onClick={handleProfile}
            className="profile-dropdown-item w-full text-left px-2.5 py-1.5 flex items-center gap-2 text-[12px] text-foreground hover:bg-secondary rounded-md transition-colors cursor-pointer"
          >
            <UserRoundCog className="w-3.5 h-3.5 text-muted-foreground pointer-events-none" />
            My Profile
          </button>
          <button
            type="button"
            role="menuitem"
            onClick={handleSignOut}
            className="profile-dropdown-item w-full text-left px-2.5 py-1.5 flex items-center gap-2 text-[12px] text-foreground hover:bg-secondary rounded-md transition-colors cursor-pointer"
          >
            <LogOut className="w-3.5 h-3.5 text-muted-foreground pointer-events-none" />
            Sign out
          </button>
        </div>
      </div>
    </>,
    document.body
  );
}
