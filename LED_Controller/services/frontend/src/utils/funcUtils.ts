const partial = (func: Function, args: any[]): Function => {
    return (...funcArgs: any[]) => func(...args, ...funcArgs);
}

export default partial;
