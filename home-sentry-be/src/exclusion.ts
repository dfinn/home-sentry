import Point from "./point";

interface Exclusion {
  id: string,
  name: string,
  top_left: Point,
  bottom_right: Point,
  threshold: number
}

export default Exclusion;