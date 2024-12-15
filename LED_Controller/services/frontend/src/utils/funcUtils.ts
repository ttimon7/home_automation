const partial = (func: Function, args: any[]): Function => {
    return (...funcArgs: any[]) => func(...args, ...funcArgs);
}

export const vw = () => Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
export const vh = () => Math.max(document.documentElement.clientHeight || 0, window.innerHeight || 0);
export const convertRemToPixels = (rem: number) => {    
    return rem * parseFloat(getComputedStyle(document.documentElement).fontSize);
}


export default partial;
