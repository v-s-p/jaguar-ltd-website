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
  categories?: string[];       // multi-list: ["Aluminium", "PVC"]
  primary_category?: string;   // display badge (ALUMINIUM / PVC)
  subcategory?: string;        // level-2: "Machining Centers", "Cutting", ...
  sub_subcategory?: string;    // level-3: "Double Head Cutting", "Radial Cutting", ...
  diller?: Record<string, any>;
  specs?: MachineSpecs;
  [key: string]: any;          // forward-compat for extra fields
}
