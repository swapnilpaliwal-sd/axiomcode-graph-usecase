type DeleteHook = (user: string, id: number) => void;

const onDelete: DeleteHook[] = [];

export function whenDeleted(hook: DeleteHook): void {
  onDelete.push(hook);
}

export function deleted(user: string, id: number): void {
  for (const hook of onDelete) hook(user, id);
}
