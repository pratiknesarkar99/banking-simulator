import {
    createContext,
    useContext,
    useEffect,
    useState,
    type ReactNode,
} from "react";

export type Theme = "dark" | "light";

interface ChartPalette {
    accent: string;
    axis: string;
    grid: string;
    tooltipBg: string;
    tooltipBorder: string;
}

export const CHART_COLORS: Record<Theme, ChartPalette> = {
    dark: {
        accent: "#e8b94a",
        axis: "#8a95a5",
        grid: "#242e3a",
        tooltipBg: "#1c242e",
        tooltipBorder: "#242e3a",
    },
    light: {
        accent: "#a8791b",
        axis: "#6d7684",
        grid: "#ddd8cc",
        tooltipBg: "#ffffff",
        tooltipBorder: "#ddd8cc",
    },
};

interface ThemeContextValue {
    theme: Theme;
    toggle: () => void;
}

const ThemeContext = createContext<ThemeContextValue>({
    theme: "dark",
    toggle: () => { },
});

function initialTheme(): Theme {
    const stored = localStorage.getItem("theme");
    if (stored === "light" || stored === "dark") return stored;
    return window.matchMedia("(prefers-color-scheme: light)").matches
        ? "light"
        : "dark";
}

export function ThemeProvider({ children }: { children: ReactNode }) {
    const [theme, setTheme] = useState<Theme>(initialTheme);

    useEffect(() => {
        document.documentElement.dataset.theme = theme;
        localStorage.setItem("theme", theme);
    }, [theme]);

    return (
        <ThemeContext.Provider
            value={{
                theme,
                toggle: () => setTheme((t) => (t === "dark" ? "light" : "dark")),
            }}
        >
            {children}
        </ThemeContext.Provider>
    );
}

export function useTheme() {
    return useContext(ThemeContext);
}