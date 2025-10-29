
import { useEffect, useState } from "react";

interface Compound {
  [key: string]: string | number;
}

export function App() {
  const [data, setData] = useState<Compound[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("http://localhost:8000/data")
      .then((res) => {
        if (!res.ok) throw new Error("Error al obtener datos del backend");
        return res.json();
      })
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  if (error) return <p style={{ color: "red" }}>{error}</p>;
  if (!data.length) return <p>Cargando datos...</p>;

  const headers = Object.keys(data[0]);

  return (
    <div style={{ padding: "1rem" }}>
      <h2>Vista previa de datos procesados</h2>
      <table border={1} cellPadding={5}>
        <thead>
          <tr>
            {headers.map((h) => (
              <th key={h}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i}>
              {headers.map((h) => (
                <td key={h}>{String(row[h])}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
