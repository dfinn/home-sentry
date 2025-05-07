import Exclusion from "./exclusion";
import Zone from "./zone";

interface SourceDefinition {
  id: string,
  name: string,
  type: string,
  url: string,
  enabled: boolean,
  exclusions: Array<Exclusion>,
  zones: Array<Zone>
}

export default SourceDefinition;