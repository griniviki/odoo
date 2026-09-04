declare module "@web/core/network/rpc" {
  export const rpc: (route: string, params?: any) => Promise<any>;
}


