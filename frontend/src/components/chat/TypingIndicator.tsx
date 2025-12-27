export function TypingIndicator() {
  return (
    <div className="flex items-center gap-3 p-4 bg-muted/50">
      <div className="flex items-center space-x-1">
        <div className="w-2 h-2 bg-primary rounded-full animate-typing" style={{ animationDelay: '0ms' }}></div>
        <div className="w-2 h-2 bg-primary rounded-full animate-typing" style={{ animationDelay: '200ms' }}></div>
        <div className="w-2 h-2 bg-primary rounded-full animate-typing" style={{ animationDelay: '400ms' }}></div>
      </div>
      <span className="text-sm text-muted-foreground">Yazıyor...</span>
    </div>
  );
}
