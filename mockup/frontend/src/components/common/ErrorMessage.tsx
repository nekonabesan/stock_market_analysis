type Props = {
  message: string;
};

export function ErrorMessage({ message }: Props) {
  return <div className="panel error-panel">{message}</div>;
}