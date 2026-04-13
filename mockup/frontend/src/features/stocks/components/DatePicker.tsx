interface DatePickerProps {
  label: string;
  value: string;
  onChange: (date: string) => void;
}

export function DatePicker({ label, value, onChange }: DatePickerProps) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
  };

  return (
    <div className="form-group">
      <label htmlFor={`date-picker-${label}`}>{label}</label>
      <input
        id={`date-picker-${label}`}
        type="date"
        value={value}
        onChange={handleChange}
      />
    </div>
  );
}
