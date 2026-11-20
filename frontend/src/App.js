import { useEffect } from "react";

export default function App() {
  useEffect(() => {
    window.location.replace("/game/index.html");
  }, []);
  return null;
}
