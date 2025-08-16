// Example TypeScript file for testing LSP functionality

interface Person {
    name: string;
    age: number;
}

class ExampleClass {
    private name: string;
    private count: number;
    
    constructor(name: string) {
        this.name = name;
        this.count = 0;
    }
    
    public greet(): string {
        return `Hello, ${this.name}!`;
    }
    
    public increment(): void {
        this.count++;
    }
}

function exampleFunction(x: number, y: number): number {
    return x + y;
}

const globalConfig: Record<string, any> = {
    debug: true,
    version: "1.0.0"
};

export { ExampleClass, exampleFunction, globalConfig, Person };