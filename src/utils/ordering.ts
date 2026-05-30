import orderingData from '../data/ordering.json';

type OrderingData = typeof orderingData;

function getOrdering(): OrderingData {
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
