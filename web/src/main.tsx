import { createRoot } from "react-dom/client";
import { Provider } from "react-redux";
import App from "./app/App.tsx";
import { store } from "./store";
import "./styles/index.css";
import { applyTheme, readPersistedTheme } from "./lib/theme";

applyTheme(readPersistedTheme());

createRoot(document.getElementById("root")!).render(
  <Provider store={store}>
    <App />
  </Provider>
);
