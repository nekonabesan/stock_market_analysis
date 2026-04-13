import { DatePicker } from "./DatePicker";

interface EndProps {
  value: string;
  onChange: (date: string) => void;
}

export function End({ value, onChange }: EndProps) {
  return (
    <DatePicker
      label="データ取得終了期間"
      value={value}
      onChange={onChange}
    />
  );
}
