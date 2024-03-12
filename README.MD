git commit -m ""

MQAgent本身並沒有
新增 packet_controller.py 當中的R

原先是使用callback function的方式來得知MQAgent的狀態，但每多一種狀態就需要一個新的callback function不利於擴充，因此使用依賴注入的方式改變原有的方式。



git commit -m "Originally, the callback function was used to know the status of the MQAgent, but each additional state required a new callback function, which was not conducive to expansion, so dependency injection was used to change the original method."

刪除一些註解掉無用的程式

將封包的生命週期用類似數位邏輯方式定義