"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

interface DatasetContextValue {
  datasetId: number | null;
  setDatasetId: (id: number | null) => void;
}

const DatasetContext = createContext<DatasetContextValue>({
  datasetId: null,
  setDatasetId: () => {},
});

const STORAGE_KEY = "signallens.current_dataset_id";

export function DatasetProvider({ children }: { children: ReactNode }) {
  const [datasetId, setDatasetIdState] = useState<number | null>(null);

  useEffect(() => {
    const stored = typeof window !== "undefined" ? window.localStorage.getItem(STORAGE_KEY) : null;
    if (stored) setDatasetIdState(Number(stored));
  }, []);

  const setDatasetId = (id: number | null) => {
    setDatasetIdState(id);
    if (typeof window !== "undefined") {
      if (id === null) window.localStorage.removeItem(STORAGE_KEY);
      else window.localStorage.setItem(STORAGE_KEY, String(id));
    }
  };

  return (
    <DatasetContext.Provider value={{ datasetId, setDatasetId }}>{children}</DatasetContext.Provider>
  );
}

export function useDataset() {
  return useContext(DatasetContext);
}
