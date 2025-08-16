// Example JavaScript file for testing LSP functionality

class ExampleClass {
    constructor(name) {
        this.name = name;
        this.count = 0;
    }
    
    greet() {
        return `Hello, ${this.name}!`;
    }
    
    increment() {
        this.count++;
    }
}

function exampleFunction(x, y) {
    return x + y;
}

const globalConfig = {
    debug: true,
    version: "1.0.0"
};

export { ExampleClass, exampleFunction, globalConfig };