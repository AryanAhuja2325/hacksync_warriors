import { LogOut, User as UserIcon, Bell, Settings, Target, TrendingUp } from "lucide-react";

export default function Navbar({ currentView = "start", onViewChange }) {
  const user = JSON.parse(localStorage.getItem("user") || "null");

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    window.location.reload();
  };

  return (
    <header className="top-navbar">
      <div className="brand">
        <div className="brand-dot" />
        <span className="brand-text">BrandPulse 2.0</span>

        <div className="top-nav-items">
          <button
            className={
              currentView === "start" ? "nav-item nav-item-active" : "nav-item"
            }
            onClick={() => onViewChange?.("start")}
            style={{ fontSize: "0.8rem", padding: "0.25rem 0.75rem" }}
          >
            Studio
          </button>
          <button
            className={
              currentView === "canvas" ? "nav-item nav-item-active" : "nav-item"
            }
            onClick={() => onViewChange?.("canvas")}
            style={{ fontSize: "0.8rem", padding: "0.25rem 0.75rem" }}
          >
            Campaigns
          </button>

          <button
            className={
              currentView === "analytics" ? "nav-item nav-item-active" : "nav-item"
            }
            onClick={() => onViewChange?.("analytics")}
            style={{
              fontSize: "0.8rem",
              padding: "0.25rem 0.75rem",
              display: "flex",
              alignItems: "center",
              gap: "0.4rem",
            }}
          >
            <TrendingUp style={{ width: "0.9rem", height: "0.9rem" }} />
            Analytics
          </button>
          
          <button
            className={
              currentView === "insights"
                ? "nav-item nav-item-active"
                : "nav-item"
            }
            onClick={() => onViewChange?.("insights")}
            style={{
              fontSize: "0.8rem",
              padding: "0.25rem 0.75rem",
              display: "flex",
              alignItems: "center",
              gap: "0.4rem",
            }}
          >
            <Target style={{ width: "0.9rem", height: "0.9rem" }} />
            Competitors
          </button>
        </div>
      </div>

      <div className="top-navbar-right">
        <button
          style={{
            all: "unset",
            cursor: "pointer",
            padding: "0.4rem",
            borderRadius: "0.5rem",
            display: "flex",
          }}
        >
          <Bell
            style={{ width: "1.1rem", height: "1.1rem", color: "#9ca3af" }}
          />
        </button>
        <button
          style={{
            all: "unset",
            cursor: "pointer",
            padding: "0.4rem",
            borderRadius: "0.5rem",
            display: "flex",
          }}
        >
          <Settings
            style={{ width: "1.1rem", height: "1.1rem", color: "#9ca3af" }}
          />
        </button>

        <div
          style={{
            width: "1px",
            height: "1.5rem",
            background: "rgba(148, 163, 184, 0.2)",
            margin: "0 0.5rem",
          }}
        />

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "0.75rem",
            padding: "0.25rem 0.5rem",
            borderRadius: "0.75rem",
            background: "rgba(255, 255, 255, 0.04)",
          }}
        >
          {user?.photoURL ? (
            <img
              src={user.photoURL}
              alt="Avatar"
              style={{
                width: "1.75rem",
                height: "1.75rem",
                borderRadius: "50%",
                border: "1px solid rgba(56, 189, 248, 0.4)",
              }}
            />
          ) : (
            <div
              style={{
                width: "1.75rem",
                height: "1.75rem",
                borderRadius: "50%",
                background: "rgba(255, 255, 255, 0.1)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <UserIcon
                style={{ width: "1rem", height: "1rem", color: "#9ca3af" }}
              />
            </div>
          )}
          <div style={{ display: "flex", flexDirection: "column" }}>
            <span
              style={{
                color: "#e5e7eb",
                fontSize: "0.8rem",
                fontWeight: "600",
                lineHeight: 1,
              }}
            >
              {user?.email?.split("@")[0] || "User"}
            </span>
            <span
              style={{
                color: "#64748b",
                fontSize: "0.65rem",
                fontWeight: "500",
              }}
            >
              Pro Plan
            </span>
          </div>
        </div>

        <button
          onClick={handleLogout}
          title="Logout"
          style={{
            all: "unset",
            cursor: "pointer",
            padding: "0.4rem",
            borderRadius: "0.5rem",
            display: "flex",
            background: "rgba(239, 68, 68, 0.08)",
            border: "1px solid rgba(239, 68, 68, 0.15)",
            transition: "all 0.2s",
          }}
          onMouseOver={(e) =>
            (e.currentTarget.style.background = "rgba(239, 68, 68, 0.15)")
          }
          onMouseOut={(e) =>
            (e.currentTarget.style.background = "rgba(239, 68, 68, 0.08)")
          }
        >
          <LogOut
            style={{ width: "1.1rem", height: "1.1rem", color: "#f87171" }}
          />
        </button>
      </div>
    </header>
  );
}
