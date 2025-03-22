#pragma once

namespace fcp {
class ISensorService {
    public:
        virtual SensorInformation RequestState(SensorReq& input) = 0;
        virtual Temperature GetTemperature(SensorReq& input) = 0;
};
}
