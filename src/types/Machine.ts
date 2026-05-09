export interface MachineSpecs {
  "STANDART AKSESUARLAR"?: string[];
  "OPSIYONEL AKSESUARLAR"?: string[];
  "GENEL OZELLIKLER"?: string[];
  "TEKNIK_TABLO"?: Record<string, string>;
}

export interface Machine {
  id: string;
  name?: string;
  slug?: string;
  brand?: string;
  categories?: string[];
  subcategory: string[];
  specs?: MachineSpecs;
  [key: string]: any; // Allow other properties as needed
}
