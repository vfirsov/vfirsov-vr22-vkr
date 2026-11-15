export interface Tea {
  id: number
  slug: string
  name: string
  category: string
  origin: string
  description: string
  price: number
  weightGrams: number
  inStock: boolean
}

export interface Catalog {
  items: Tea[]
  total: number
  currency: 'RUB'
}
