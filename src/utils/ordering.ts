import orderingRaw from '../data/ordering.json';

interface MaterialSubcategoryEntry {
  material: string;
  subcategories: string[];
}

interface MachineOrderEntry {
  material: string;
  subcategory: string;
  machines: string[];
}

interface OrderingConfig {
  header_dropdown: string[];
  subcategories_per_material: MaterialSubcategoryEntry[];
  machines_per_subcategory: MachineOrderEntry[];
  header_subcategory_override?: MaterialSubcategoryEntry[];
}

const orderingData = orderingRaw as unknown as OrderingConfig;

function getOrdering(): OrderingConfig {
  return orderingData;
}

/** Sort items by a reference order list, unknown items appended alphabetically. */
export function sortByOrder<T>(
  items: T[],
  orderList: string[],
  keyFn: (item: T) => string
): T[] {
  const indexMap = new Map(orderList.map((val, i) => [val, i]));
  return [...items].sort((a, b) => {
    const ai = indexMap.get(keyFn(a)) ?? Infinity;
    const bi = indexMap.get(keyFn(b)) ?? Infinity;
    if (ai !== bi) return ai - bi;
    // Alphabetical fallback for items not in ordering list
    return keyFn(a).localeCompare(keyFn(b));
  });
}

export function getMaterialOrder(): string[] {
  return getOrdering().header_dropdown;
}

export function getSubcategoryOrder(material: string): string[] {
  const entry = getOrdering().subcategories_per_material.find(
    (e) => e.material === material
  );
  return entry?.subcategories ?? [];
}

export function getMachineOrder(material: string, subcategory: string): string[] {
  const entry = getOrdering().machines_per_subcategory.find(
    (e) => e.material === material && e.subcategory === subcategory
  );
  return entry?.machines ?? [];
}

/**
 * Returns the subcategory order for the header mega-menu.
 * If header_subcategory_override has an entry for this material, uses that.
 * Otherwise falls back to subcategories_per_material (same as category page).
 */
export function getHeaderSubcategoryOrder(material: string): string[] {
  const overrides = getOrdering().header_subcategory_override;
  if (overrides) {
    const override = overrides.find((o) => o.material === material);
    if (override?.subcategories?.length) return override.subcategories;
  }
  return getSubcategoryOrder(material);
}
