type Props = {
  active: boolean;
};

export function RiseSignalBadge({ active }: Props) {
  return (
    <span className={active ? "signal-badge signal-on" : "signal-badge signal-off"}>
      {active ? "Rise Signal On" : "Rise Signal Off"}
    </span>
  );
}