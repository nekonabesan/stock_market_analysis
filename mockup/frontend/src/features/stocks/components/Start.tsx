import { DatePicker } from "./DatePicker";

interface StartProps {
  value: string;
  onChange: (date: string) => void;
}

export function Start({ value, onChange }: StartProps) {
  return (
    <DatePicker
      label="データ取得開始期間"
      value={value}
      onChange={onChange}
    />
  );
}
